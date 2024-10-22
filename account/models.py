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
            name=name,
            terms_conditions=terms_conditions,
        )

        user.set_password(password)

        user.is_admin = True
        user.is_approved = True 
        user.is_active = True 
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
    _password_set = False  

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
    # Hash the password only if it's being set and is not already hashed
        if self.pk is None or (self._password_set and not self.password.startswith('pbkdf2_')):
            self.set_password(self.password)  # Hash the password
            self._password_set = False  # Reset flag after hashing
        super(User, self).save(*args, **kwargs)


    def set_password(self, raw_password):
        super().set_password(raw_password)
        self._password_set = True  

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
    


class Guarantor(models.Model):
    # Guarantor 1 Fields
    cnic_no = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    residential_address = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    monthly_income = models.IntegerField(blank=True, null=True)
    office_address = models.CharField(max_length=250, blank=True, null=True)
    office_phone = models.CharField(max_length=100, blank=True, null=True)
    phone_no = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} (CNIC: {self.cnic_no})"


