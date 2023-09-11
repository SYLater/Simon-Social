from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, user_email, password=None, **extra_fields):
        if not user_email:
            raise ValueError('The Email field must be set')
        user = self.model(user_email=self.normalize_email(user_email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(user_email, password, **extra_fields)

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_email = models.EmailField(unique=True)
    user_firstName = models.CharField(max_length=50)
    user_middleName = models.CharField(max_length=50, blank=True, null=True)
    user_lastName = models.CharField(max_length=50)
    user_userName = models.CharField(max_length=50, unique=True)
    user_birthDay = models.DateField(null=True, blank=True)
    user_is_teacher = models.BooleanField(null=True, blank=True)
    user_joinDate = models.DateField(null=True, blank=True)
    user_status = models.BooleanField(null=True, blank=True)
    user_icon = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    cookies = models.TextField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = []

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    studentGUID = models.CharField(max_length=100, null=True, blank=True)
    communityID = models.CharField(max_length=100, null=True, blank=True)
    communityUID = models.CharField(max_length=100, null=True, blank=True)
    FullName = models.CharField(max_length=100, null=True, blank=True)
    YearLevelCode = models.CharField(max_length=10, null=True, blank=True)
    HouseDescription = models.CharField(max_length=100, null=True, blank=True)
    HomeroomCode = models.CharField(max_length=20, null=True, blank=True)
    HomeroomDescription = models.CharField(max_length=100, null=True, blank=True)
    HomeroomTeachers = models.TextField(null=True, blank=True)
    StudentID = models.CharField(max_length=50, null=True, blank=True)
    StudentPersonalRefId = models.CharField(max_length=50, null=True, blank=True)
    NoteCount = models.IntegerField(null=True, blank=True)
    NoteImportantCount = models.IntegerField(null=True, blank=True)
    ImportantMedicalWarning = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user_userName

class UserFriendsRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rel')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_rel')

    def __str__(self):
        return f"{self.user} - {self.friend}"

class UserClassesRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_classes')
    class_id = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user} - {self.class_id}"
