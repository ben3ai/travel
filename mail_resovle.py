from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import re

class MailResovle:
    def resovle_to_mail(self, msg_content) -> dict:
        msg = Parser().parsestr(msg_content) # 稍后解析出邮件:
        if self.__check_mail(msg) == False:
            return {}
        order_type = self.__train_type(msg)
        order_id, order_info = self.__mail_content(msg)
        if len(order_id) > 0 and len(order_type) > 0 or len(order_info) > 0:
            return {"order_id": order_id, "order_type": order_type, "order_info": order_info}
        else:
            return {}

    def __mail_content(self, msg):
        if msg.is_multipart():
            parts = msg.get_payload()
            if len(parts) > 0:
                return self.__mail_content_html(parts[0])
        return '',''

    def __mail_content_html(self, msg):
        content_type = msg.get_content_type()
        if 'text/plain' in content_type or 'text/html' in content_type:
            charset = self.__content_charset(msg)
            if charset:
                content = msg.get_payload(decode=True).decode(charset)
                return self.__get_order_info(content)
        return '',''

    def __get_order_info(self, content_html):
        order_id = ''
        order_info_str = ''
        result = re.search(r'订单号码([A-Za-z0-9\s]*)',content_html,re.DOTALL)
        if not result is None:
            order_id = result.group(1).strip()
        result = re.search(r'车票信息如下(?:\uFF1A|:)\s+(.*)\s+(?:为了确保|按购票时){1}',content_html,re.DOTALL)
        if not result is None:
            order_info_str = result.group(1).strip()
        return order_id, order_info_str

    def __train_type(self, msg):
        subject = self.__decode_str(msg.get('Subject', ''))
        if "支付通知" in subject or "兑现成功通知" in subject:
            return 'insert'
        elif "改签通知" in subject:
            return 'modify'
        elif "退票通知" in subject:
            return 'delete'
        return ''

    def __content_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def __decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def __check_mail(self, msg) -> bool:
        _, from_address = parseaddr(msg.get('From', ''))
        return '12306@rails.com.cn' in from_address or 'ben3ai@gmail.com' in from_address
