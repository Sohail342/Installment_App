from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class MyUserManager(BaseUserManager):
    def create_user(self, email, name, terms_conditions, password=None, password2=None):
        """
        Creates and saves a User with the given email, terms_conditions
        name and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            terms_conditions = terms_conditions,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, terms_conditions, password=None):
        """
        Creates and saves a superuser with the given email, name,  terms_conditions
        and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            terms_conditions=terms_conditions,
        )
        user.is_admin = True
        user.is_approved = True 
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    terms_conditions = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "terms_conditions"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    def save(self, *args, **kwargs):
        if self.pk is None:  # User is being created
            self.set_password(self.password)  # Hash the password
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Sales Team"
    

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    cnic = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


