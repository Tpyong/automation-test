"""
测试数据工厂模块
使用 Faker 生成真实的测试数据
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from faker import Faker

from core.utils.logger import get_logger

logger = get_logger(__name__)


class DataFactory:
    """测试数据工厂"""

    def __init__(self, locale: str = "zh_CN"):
        """
        初始化数据工厂

        Args:
            locale: 本地化设置（zh_CN, en_US 等）
        """
        self.fake = Faker(locale)
        logger.info(f"数据工厂初始化完成，locale: {locale}")

    # ==================== 用户相关数据 ====================

    def generate_user(self, **kwargs) -> Dict[str, Any]:
        """
        生成用户数据

        Args:
            **kwargs: 自定义字段值

        Returns:
            用户数据字典
        """
        user = {
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password(length=10, special_chars=True, digits=True),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "phone": self.fake.phone_number(),
            "address": self.fake.address(),
            "city": self.fake.city(),
            "country": self.fake.country(),
            "postcode": self.fake.postcode(),
            "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
            "updated_at": self.fake.date_time_between(start_date="-1m", end_date="now"),
            "is_active": random.choice([True, False]),
            "role": random.choice(["user", "admin", "moderator"]),
        }
        user.update(kwargs)
        logger.debug(f"生成用户数据: {user['username']}")
        return user

    def generate_users(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        生成多个用户数据

        Args:
            count: 生成数量
            **kwargs: 自定义字段值

        Returns:
            用户数据列表
        """
        return [self.generate_user(**kwargs) for _ in range(count)]

    # ==================== 商品相关数据 ====================

    def generate_product(self, **kwargs) -> Dict[str, Any]:
        """
        生成商品数据

        Args:
            **kwargs: 自定义字段值

        Returns:
            商品数据字典
        """
        product = {
            "product_id": self.fake.uuid4(),
            "name": self.fake.word().title() + " " + self.fake.word().title(),
            "description": self.fake.text(max_nb_chars=200),
            "price": round(random.uniform(10.0, 1000.0), 2),
            "original_price": round(random.uniform(20.0, 2000.0), 2),
            "stock": random.randint(0, 1000),
            "category": random.choice(["电子产品", "服装", "食品", "家居", "图书", "运动"]),
            "brand": self.fake.company(),
            "sku": self.fake.ean13(),
            "weight": round(random.uniform(0.1, 50.0), 2),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "reviews_count": random.randint(0, 10000),
            "is_featured": random.choice([True, False]),
            "is_available": random.choice([True, False]),
            "created_at": self.fake.date_time_between(start_date="-2y", end_date="now"),
            "updated_at": self.fake.date_time_between(start_date="-1m", end_date="now"),
        }
        product.update(kwargs)
        logger.debug(f"生成商品数据: {product['name']}")
        return product

    def generate_products(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        生成多个商品数据

        Args:
            count: 生成数量
            **kwargs: 自定义字段值

        Returns:
            商品数据列表
        """
        return [self.generate_product(**kwargs) for _ in range(count)]

    # ==================== 订单相关数据 ====================

    def generate_order(self, **kwargs) -> Dict[str, Any]:
        """
        生成订单数据

        Args:
            **kwargs: 自定义字段值

        Returns:
            订单数据字典
        """
        order_date = self.fake.date_time_between(start_date="-1y", end_date="now")
        total_amount = round(random.uniform(50.0, 5000.0), 2)

        order = {
            "order_id": self.fake.uuid4(),
            "order_number": self.fake.ean13(),
            "user_id": self.fake.uuid4(),
            "items": self.generate_order_items(random.randint(1, 10)),
            "total_amount": total_amount,
            "discount_amount": round(random.uniform(0.0, total_amount * 0.3), 2),
            "tax_amount": round(total_amount * 0.1, 2),
            "shipping_address": self.fake.address(),
            "billing_address": self.fake.address(),
            "payment_method": random.choice(["信用卡", "支付宝", "微信支付", "PayPal"]),
            "payment_status": random.choice(["待支付", "已支付", "支付失败", "已退款"]),
            "order_status": random.choice(["待处理", "处理中", "已发货", "已送达", "已取消"]),
            "shipping_method": random.choice(["标准配送", "加急配送", "次日达"]),
            "tracking_number": self.fake.ean13(),
            "estimated_delivery": order_date + timedelta(days=random.randint(1, 7)),
            "actual_delivery": order_date + timedelta(days=random.randint(1, 10)),
            "notes": self.fake.text(max_nb_chars=100),
            "created_at": order_date,
            "updated_at": self.fake.date_time_between(start_date=order_date, end_date="now"),
        }
        order.update(kwargs)
        logger.debug(f"生成订单数据: {order['order_number']}")
        return order

    def generate_order_items(self, count: int) -> List[Dict[str, Any]]:
        """
        生成订单项数据

        Args:
            count: 订单项数量

        Returns:
            订单项列表
        """
        items = []
        for _ in range(count):
            item = {
                "item_id": self.fake.uuid4(),
                "product_id": self.fake.uuid4(),
                "product_name": self.fake.word().title() + " " + self.fake.word().title(),
                "quantity": random.randint(1, 5),
                "unit_price": round(random.uniform(10.0, 1000.0), 2),
                "subtotal": 0.0,
            }
            item["subtotal"] = round(item["quantity"] * item["unit_price"], 2)
            items.append(item)
        return items

    # ==================== 支付相关数据 ====================

    def generate_payment(self, **kwargs) -> Dict[str, Any]:
        """
        生成支付数据

        Args:
            **kwargs: 自定义字段值

        Returns:
            支付数据字典
        """
        payment = {
            "payment_id": self.fake.uuid4(),
            "order_id": self.fake.uuid4(),
            "amount": round(random.uniform(50.0, 5000.0), 2),
            "currency": random.choice(["CNY", "USD", "EUR", "GBP", "JPY"]),
            "payment_method": random.choice(["信用卡", "支付宝", "微信支付", "PayPal"]),
            "card_number": self.fake.credit_card_number(),
            "card_expiry": self.fake.credit_card_expire(),
            "card_cvv": self.fake.credit_card_security_code(),
            "transaction_id": self.fake.uuid4(),
            "status": random.choice(["pending", "success", "failed", "refunded"]),
            "failure_reason": random.choice(["余额不足", "卡片过期", "网络错误", "验证失败", None]),
            "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
            "updated_at": self.fake.date_time_between(start_date="-1m", end_date="now"),
        }
        payment.update(kwargs)
        logger.debug(f"生成支付数据: {payment['transaction_id']}")
        return payment

    # ==================== 地址相关数据 ====================

    def generate_address(self, **kwargs) -> Dict[str, Any]:
        """
        生成地址数据

        Args:
            **kwargs: 自定义字段值

        Returns:
            地址数据字典
        """
        address = {
            "address_id": self.fake.uuid4(),
            "user_id": self.fake.uuid4(),
            "full_name": self.fake.name(),
            "phone": self.fake.phone_number(),
            "address_line1": self.fake.street_address(),
            "address_line2": random.choice([None, self.fake.secondary_address()]),
            "city": self.fake.city(),
            "state": self.fake.province(),
            "postcode": self.fake.postcode(),
            "country": self.fake.country(),
            "is_default": random.choice([True, False]),
            "address_type": random.choice(["home", "work", "other"]),
            "created_at": self.fake.date_time_between(start_date="-2y", end_date="now"),
            "updated_at": self.fake.date_time_between(start_date="-1m", end_date="now"),
        }
        address.update(kwargs)
        logger.debug(f"生成地址数据: {address['city']}")
        return address

    # ==================== 通用数据生成 ====================

    def random_int(self, min_value: int, max_value: int) -> int:
        """生成随机整数"""
        return random.randint(min_value, max_value)

    def random_float(self, min_value: float, max_value: float, decimals: int = 2) -> float:
        """生成随机浮点数"""
        return round(random.uniform(min_value, max_value), decimals)

    def random_choice(self, choices: List[Any]) -> Any:
        """从列表中随机选择"""
        return random.choice(choices)

    def random_boolean(self) -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])

    def random_date(self, start_date: str = "-1y", end_date: str = "now") -> datetime:
        """
        生成随机日期

        Args:
            start_date: 开始日期（相对或绝对）
            end_date: 结束日期（相对或绝对）

        Returns:
            日期对象
        """
        return self.fake.date_time_between(start_date=start_date, end_date=end_date)

    def random_word(self) -> str:
        """生成随机单词"""
        return self.fake.word()

    def random_sentence(self, nb_words: int = 10) -> str:
        """生成随机句子"""
        return self.fake.sentence(nb_words=nb_words)

    def random_paragraph(self, nb_sentences: int = 3) -> str:
        """生成随机段落"""
        return self.fake.paragraph(nb_sentences=nb_sentences)

    def random_email(self) -> str:
        """生成随机邮箱"""
        return self.fake.email()

    def random_phone(self) -> str:
        """生成随机手机号"""
        return self.fake.phone_number()

    def random_name(self) -> str:
        """生成随机姓名"""
        return self.fake.name()

    def random_company(self) -> str:
        """生成随机公司名"""
        return self.fake.company()

    def random_uuid(self) -> str:
        """生成随机UUID"""
        return self.fake.uuid4()


# 全局数据工厂实例
_factory = None


def get_data_factory(locale: str = "zh_CN") -> DataFactory:
    """
    获取全局数据工厂实例

    Args:
        locale: 本地化设置

    Returns:
        数据工厂实例
    """
    global _factory
    if _factory is None:
        _factory = DataFactory(locale)
    return _factory
