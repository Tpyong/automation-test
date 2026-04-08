"""
模型模块
定义测试中使用的数据模型
"""

from typing import Any, Dict, List, Optional


class BaseModel:
    """基础模型类"""

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型转换为字典

        Returns:
            模型的字典表示
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __str__(self) -> str:
        """返回模型的字符串表示"""
        return f"{self.__class__.__name__}({self.to_dict()})"


class User(BaseModel):
    """用户模型"""

    def __init__(self, id: int, username: str, email: str, **kwargs):
        """
        初始化用户模型

        Args:
            id: 用户 ID
            username: 用户名
            email: 邮箱
            password: 密码
            name: 姓名
            age: 年龄
            role: 角色
        """
        self.id = id
        self.username = username
        self.email = email
        self.password = kwargs.get("password")
        self.name = kwargs.get("name")
        self.age = kwargs.get("age")
        self.role = kwargs.get("role", "user")


class Product(BaseModel):
    """产品模型"""

    def __init__(self, id: int, name: str, price: float, **kwargs):
        """
        初始化产品模型

        Args:
            id: 产品 ID
            name: 产品名称
            price: 价格
            description: 描述
            stock: 库存
            category: 分类
        """
        self.id = id
        self.name = name
        self.price = price
        self.description = kwargs.get("description")
        self.stock = kwargs.get("stock", 0)
        self.category = kwargs.get("category")


class Order(BaseModel):
    """订单模型"""

    def __init__(self, id: int, user_id: int, products: List[Dict[str, Any]], total_amount: float, **kwargs):
        """
        初始化订单模型

        Args:
            id: 订单 ID
            user_id: 用户 ID
            products: 产品列表
            total_amount: 总金额
            status: 状态
            created_at: 创建时间
        """
        self.id = id
        self.user_id = user_id
        self.products = products
        self.total_amount = total_amount
        self.status = kwargs.get("status", "pending")
        self.created_at = kwargs.get("created_at")


class TestData(BaseModel):
    """测试数据模型"""

    def __init__(
        self,
        name: str,
        data: Dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        初始化测试数据模型

        Args:
            name: 测试数据名称
            data: 测试数据
            description: 描述
            tags: 标签
        """
        self.name = name
        self.data = data
        self.description = description
        self.tags = tags or []
