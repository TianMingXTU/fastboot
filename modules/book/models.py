# modules/book/models.py
from tortoise.models import Model
from tortoise import fields

class BookOrm(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, description="书籍标题")
    author = fields.CharField(max_length=100, null=True)
    isbn = fields.CharField(max_length=20, unique=True, null=True, description="国际标准书号")
    pages = fields.IntField(null=True, default=0)
    is_published = fields.BooleanField(default=False)
    published_on = fields.DateField(null=True)
    # created_at = fields.DatetimeField(auto_now_add=True) # 示例时间戳