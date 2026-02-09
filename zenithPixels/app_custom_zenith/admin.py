from django.contrib import admin
from .models import PostCategory, DevlogPost, PostLike, PostComment

admin.site.register(PostCategory)
admin.site.register(DevlogPost)
admin.site.register(PostLike)
admin.site.register(PostComment)