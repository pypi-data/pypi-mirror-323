import json
import time
import base64
import logging
import asyncio
import traceback

from websockets import connect
from websockets.exceptions import ConnectionClosed
from websockets.extensions.permessage_deflate import ClientPerMessageDeflateFactory

from concurrent.futures import ThreadPoolExecutor
from .config import *

# 配置主程序的日志记录器
logger = logging.getLogger("HandGPT")
logger.setLevel(logging.INFO)

# 确保只添加一次处理器
if not logger.hasHandlers():
    # 配置屏幕输出的 StreamHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # 创建格式化器并添加到处理器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

class HandGPT:
    def __init__(self, url, agent_func):
        """
        初始化 HandGPT 实例，包含 WebSocket 连接地址、agent 处理函数、线程池及事件循环。
        
        :param url: WebSocket 服务器的 URL
        :param agent_func: 用户定义的 agent 函数，用于处理接收到的任务
        """
        self.url = url
        self.ws_connection = None
        self.agent_func = agent_func
        self.executor = ThreadPoolExecutor(max_workers = WORKER_NUM)
        self.loop = asyncio.get_event_loop()  # 在初始化中定义事件循环
        self.pending_responses = {}  # 存储等待响应的消息
        self.is_reconnecting = False  # 标志是否在重连中
        logger.info("HandGPT instance created with URL: %s", url)

    async def connect(self):
        """
        连接到 WebSocket 服务器，并启动消息接收和 ping-pong 机制。
        如果连接断开，则会自动重连。
        """
        if self.is_reconnecting:  # 检查是否已有重连尝试在进行中
            return
        self.is_reconnecting = True  # 开始连接或重连

        while True:
            try:
                # 设置 WebSocket 扩展（支持压缩）
                compression = ClientPerMessageDeflateFactory()

                # 尝试连接 WebSocket 服务器
                self.ws_connection = await connect(
                    self.url,
                    extensions=[compression],  # 添加压缩支持
                    ping_interval=20,          # 定期发送 Ping 帧
                    ping_timeout=15,           # 超时时间
                    max_size=100 * 1024 * 1024, # 最大传输字节
                )
                logger.info("Connected to WebSocket server at %s", self.url)
                asyncio.create_task(self.receive_message())
                self.is_reconnecting = False  # 连接成功，清除重连标志
                break  # 成功连接后退出循环
            except ConnectionClosed as e:
                logger.warning("Connection closed: %s. Retrying in 5 seconds...", e)
                await asyncio.sleep(5)
            except Exception as e:
                logger.exception("Unexpected error during connection: %s", e)
                logger.debug(traceback.format_exc())
                await asyncio.sleep(5)  # 连接失败，等待 5 秒后重试

    def handle_exception(self, future):
        """
        捕获子线程异常并记录日志。
        
        :param future: 异步任务的 Future 对象
        """
        exception = future.exception()
        if exception:
            # 获取详细的堆栈信息
            tb_str = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            logger.error("Exception in thread task: %s\nTraceback:\n%s", exception, tb_str, exc_info=True)

    async def receive_message(self):
        """
        异步接收消息，并根据消息内容分发处理。
        """
        while True:
            try:
                async for message in self.ws_connection:
                    logger.debug("Message received: %s", message)
                    data = json.loads(message)
                    message_id = data.get("messageId")
                    logger.info("Message ID received: %s", message_id)

                    # 检查是否为请求的响应
                    if message_id and message_id in self.pending_responses:
                        # 尝试 set_result
                        try:
                            self.pending_responses[message_id].set_result(data)
                            logger.info("Response received for message ID: %s", message_id)
                        except asyncio.InvalidStateError:
                            # 如果 Future 已经被取消 (超时或者其他原因)，会出现 InvalidStateError
                            logger.warning("Future for message ID %s is already done/cancelled, ignoring duplicate response.", message_id)
                        finally:
                            # 无论 set_result 成功与否，都要从字典中删除，避免内存泄漏
                            del self.pending_responses[message_id]
                    else:
                        # 提交给 agent 处理
                        task_id = data.get("taskId")
                        task_message = data['payload'].get("message")
                        logger.info("New task received: task_id=%s, task_message=%s", task_id, task_message)
                        # 提交任务并为 Future 添加回调以捕获异常
                        future = self.executor.submit(self.agent_func, self, task_id, task_message)
                        future.add_done_callback(self.handle_exception)

            except ConnectionClosed:
                logger.warning("Connection closed while receiving message. Reconnecting...")
                await self.connect()
            except Exception as e:
                logger.error("Unexpected error while receiving message: %s", e, exc_info=True)
                logger.debug(traceback.format_exc())
                continue

    async def _send_async(self, payload):
        """异步发送消息到 WebSocket，并处理连接关闭的情况"""
        while True: # 添加循环以处理重连
            if not self.ws_connection:
                logger.error("WebSocket connection is not open. Waiting for reconnection...", exc_info=True)
                await self.connect()  # 调用重连
                await asyncio.sleep(1) # 等待重连
                continue  # 继续循环检查连接
            try:
                logger.debug("Attempting to send message asynchronously: %s", payload)
                await self.ws_connection.send(json.dumps(payload))
                logger.debug("Message sent: %s", payload)
                break # 发送成功，退出循环
            except ConnectionClosed:
                logger.warning("Connection closed during send. Waiting for reconnection...")
                self.ws_connection = None
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("Error sending message: %s", e, exc_info=True)
                break # 出现其他错误，退出循环

    def _send(self, payload):
        """同步调用异步发送，并等待发送完成"""
        future = asyncio.run_coroutine_threadsafe(self._send_async(payload), self.loop)
        try:
            future.result() # 等待发送完成
        except Exception as e:
            logger.error(f"Error during sending message: {e}", exc_info=True)

    async def _await_response_async(self, message_id, request, timeout=10):
        """异步等待响应，并处理超时"""
        future = self.loop.create_future()
        self.pending_responses[message_id] = future
        await self._send_async(request)  # 使用异步发送
        logger.info("Awaiting response for message ID: %s", message_id)

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for response to message ID: {message_id}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error waiting for response: {e}", exc_info=True)
            return None

    def _await_response(self, message_id, request, timeout=20):
        """同步包装异步等待响应"""
        try:
            result = asyncio.run_coroutine_threadsafe(
                self._await_response_async(message_id, request, timeout), self.loop
            ).result()
            return result
        except Exception as e:
            logger.error(f"Error during _await_response: {e}", exc_info=True)
            return None

    def _generate_message_id(self):
        """
        生成唯一的消息 ID，基于当前时间戳。
        """
        message_id = int(time.time() * 1000)
        logger.debug("Generated message ID: %s", message_id)
        return message_id

    def reply_message(self, task_id, message):
        """
        发送回复消息。
        
        :param task_id: 任务 ID
        :param message: 要发送的回复内容
        """
        message_id = self._generate_message_id()
        request = {
            "type": "reply_message",
            "taskId": task_id,
            "payload": {"message": message},
            "messageId": message_id
        }
        logger.info("Replying to task ID %s with message ID %s: %s", task_id, message_id, message)
        self._send(request)

    def cmd_key(self, task_id, keys):
        """
        发送键盘指令。
        
        :param task_id: 任务 ID
        :param keys: 键列表
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_key",
            "taskId": task_id,
            "payload": {"key": keys},
            "messageId": message_id
        }
        logger.info("Sending key command for task ID %s with keys %s and message ID %s", task_id, keys, message_id)
        self._send(request)

    def cmd_clipboard(self, task_id, clipboard_content):
        """
        设置剪贴板内容。
        
        :param task_id: 任务 ID
        :param clipboard_content: 要设置的剪贴板内容
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_clipboard",
            "taskId": task_id,
            "payload": clipboard_content,
            "messageId": message_id
        }
        logger.info("Setting clipboard for task ID %s with content %s", task_id, clipboard_content)
        self._send(request)

    def cmd_input(self, task_id, input_text):
        """
        发送输入文本指令。
        
        :param task_id: 任务 ID
        :param input_text: 要输入的文本
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_input",
            "taskId": task_id,
            "payload": {"input": input_text},
            "messageId": message_id
        }
        logger.info("Sending input command for task ID %s with text %s", task_id, input_text)
        self._send(request)

    def cmd_move(self, task_id, points):
        """
        发送移动指令。
        
        :param task_id: 任务 ID
        :param points: 移动的点列表
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_move",
            "taskId": task_id,
            "payload": {"point": points},
            "messageId": message_id
        }
        logger.info("Sending move command for task ID %s with points %s", task_id, points)
        self._send(request)

    def cmd_moveto(self, task_id, element_id, offset = []):
        """
        发送移动到某元素的指令。
        
        :param task_id: 任务 ID
        :param element: 元素 ID 列表
        :param offset: 偏移值列表
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_moveto",
            "taskId": task_id,
            "payload": {"elementId": element_id, "offset": offset},
            "messageId": message_id
        }
        logger.info("Sending move-to command for task ID %s with element %s and offset %s", task_id, element_id, offset)
        self._send(request)

    def cmd_click(self, task_id, element_id, offset = [], key = "left"):
        """
        发送点击指令。
        
        :param task_id: 任务 ID
        :param element: 元素 ID 列表
        :param offset: 偏移值列表
        :param key: 点击按键，包含 left, right, middle
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_click",
            "taskId": task_id,
            "payload": {"elementId": element_id, "offset": offset, "key": key},
            "messageId": message_id
        }
        logger.info("Sending click command for task ID %s with element %s and offset %s", task_id, element_id, offset)
        self._send(request)

    def cmd_longclick(self, task_id, element_id, offset = [], time_sec = 1, key = "left"):
        """
        发送长按指令。
        
        :param task_id: 任务 ID
        :param element: 元素 ID 列表
        :param offset: 偏移值列表
        :param time_sec: 长按时间（秒）
        :param key: 点击按键，包含 left, right, middle
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_longclick",
            "taskId": task_id,
            "payload": {"elementId": element_id, "offset": offset, "time": time_sec, "key": key},
            "messageId": message_id
        }
        logger.info("Sending long-click command for task ID %s with element %s, offset %s, and time %s seconds", task_id, element_id, offset, time_sec)
        self._send(request)

    def cmd_slide(self, task_id, element_id, offsets, time_sec, key = "left"):
        """
        发送滑动指令。
        
        :param task_id: 任务 ID
        :param elements: 元素 ID 列表
        :param offsets: 每个元素的偏移值列表
        :param time_sec: 滑动时间（秒）
        :param key: 点击按键，包含 left, right, middle
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_slide",
            "taskId": task_id,
            "payload": {"elementId": element_id, "offset": offsets, "time": time_sec, "key": key},
            "messageId": message_id
        }
        logger.info("Sending slide command for task ID %s with elements %s, offsets %s, and time %s seconds", task_id, element_id, offsets, time_sec)
        self._send(request)

    def cmd_back(self, task_id):
        """
        发送返回指令。
        
        :param task_id: 任务 ID
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_back",
            "taskId": task_id,
            "payload": {},
            "messageId": message_id
        }
        logger.info("Sending back command for task ID %s", task_id)
        self._send(request)

    def cmd_home(self, task_id):
        """
        发送返回主屏指令。
        
        :param task_id: 任务 ID
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_home",
            "taskId": task_id,
            "payload": {},
            "messageId": message_id
        }
        logger.info("Sending home command for task ID %s", task_id)
        self._send(request)

    def cmd_app(self, task_id, app_package):
        """
        发送打开应用的指令。
        
        :param task_id: 任务 ID
        :param app_package: 应用包名
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_app",
            "taskId": task_id,
            "payload": {"app_package": app_package},
            "messageId": message_id
        }
        logger.info("Sending app command for task ID %s with package %s", task_id, app_package)
        self._send(request)

    def get_hand_info(self, task_id):
        """
        请求 Hand 信息。
        
        :param task_id: 任务 ID
        """
        message_id = self._generate_message_id()
        request = {
            "type": "get_hand_info",
            "taskId": task_id,
            "payload": {},
            "messageId": message_id
        }
        logger.info("Requesting hand info for task ID %s with message ID %s", task_id, message_id)
        self._send(request)

    def cmd_act(self, task_id, act):
        """
        发送自定义动作的指令。
        
        :param task_id: 任务 ID
        :param act: 动作内容
        """
        message_id = self._generate_message_id()
        request = {
            "type": "cmd_act",
            "taskId": task_id,
            "payload": {"act": act},
            "messageId": message_id
        }
        logger.info("Sending act command for task ID %s with act %s", task_id, act)
        self._send(request)

    def get_image_info(self, task_id):
        message_id = self._generate_message_id()
        request = {
            "type": "get_image_info",
            "taskId": task_id,
            "messageId": message_id,
            "payload": {}
        }
        logger.info("Requesting image info for task_id: %s with message ID: %s", task_id, message_id)
        return self._await_response(message_id, request)

    def get_device_info(self, task_id):
        message_id = self._generate_message_id()
        request = {
            "type": "get_device_info",
            "taskId": task_id,
            "messageId": message_id,
            "payload": {}
        }
        logger.info("Requesting device info for task_id: %s with message ID: %s", task_id, message_id)
        result = self._await_response(message_id, request)
        return result['payload'].get('device', None)

    def get_cache(self, app_id, message):
        message_id = self._generate_message_id()
        request = {
            "type": "get_cache",
            "appId": app_id,
            "messageId": message_id,
            "payload": {"message": message}
        }
        logger.info("Requesting cache for message: %s, app_id: %s", message, app_id)
        result = self._await_response(message_id, request)
        return result['payload'].get('description'), result['payload'].get('steps'), result['payload'].get('score')
    
    def get_llm(self, model="gpt4o", system="", user="", image=[], history=None, response_type='json_object'):
        image_b64 =[]
        for img in image:
            if not isinstance(img, str):
                image_b64.append(base64.b64encode(img).decode("utf-8"))
            else:
                image_b64.append(img)
        message_id = self._generate_message_id()
        request = {
            "type": "get_llm",
            "messageId": message_id,
            "payload": {
                "model": model,
                "system": system,
                "user": user,
                "image": image_b64,
                "history": history,
                "response_type": response_type
            }
        }
        logger.info("Requesting LLM response with message ID: %s", message_id)
        result = self._await_response(message_id, request)
        return result['payload'].get('llm_say'), result['payload'].get('history')

    def cmd(self, task_id, command):
        message_id = self._generate_message_id()
        request = command
        request['taskId'] = task_id
        request['messageId'] = message_id
        logger.info("Sending command with message ID: %s", request["messageId"])
        self._send(request)

# 启动函数
def init(agent_func, user, password):
    """
    初始化 HandGPT 实例并连接到服务器。
    
    :param agent_func: 用户定义的 agent 函数，用于处理任务
    :param user: 用户名（目前未使用）
    :param password: 密码（目前未使用）
    """
    url = f"{AGENT_SERVER_PROTOCOL}://{AGENT_SERVER_URL}:{AGENT_SERVER_PORT}/{AGENT_SERVER_PATH}?user={user}&password={password}"
    logger.info("Initializing HandGPT with URL: %s", url)

    handgpt = HandGPT(url, agent_func)
    
    # 运行事件循环以保持连接
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handgpt.connect())

    # 阻塞主线程，保持事件循环活跃
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down HandGPT...")
# 测试函数
def test():
    print("HandGPT OK.")