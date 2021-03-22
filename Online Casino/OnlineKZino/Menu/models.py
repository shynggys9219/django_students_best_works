from random import randint

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.db.models import Count


class CustomUser(AbstractUser):

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    initial_balance = models.IntegerField(default=50000)
    profile_pic = models.ImageField(upload_to='profile_pics', default='profile_pics/default.jpg')
    is_banned = models.BooleanField(default=False)

    class BJboard:
        dh = list()
        ph = list()

        deck = list()
        started = False
        bet = int()
        dd = False
        banDD = False
        WJ = False

    class PT:
        started = False
        indexes_i = list()
        indexes_j = list()
        slideshow = list()
        finished = False

    def __str__(self):
        return self.username

    class Roulette:
        message = str()
        bet = int()
        fields = dict.fromkeys([i for i in range(37)], 0)
        threePart = dict.fromkeys([1, 2, 3], 0)
        twoPart = dict.fromkeys([1, 2], 0)
        color = dict.fromkeys([1, 2], 0)
        parity = dict.fromkeys([1, 2], 0)
        row = dict.fromkeys([1, 2, 3], 0)
        all_bets = int()
        slideshow = list()
        index = int()
        started = False
        finished = False

    class Ska4ki:
        started = False
        bet1 = int()
        bet2 = int()
        bet3 = int()
        bet4 = int()
        bet5 = int()
        betALLDIE = int()
        betALLALIVE = int()

    def __str__(self):
        return self.username

    class Slot:
        baraban_1 = []
        baraban_2 = []
        baraban_3 = []
        baraban_4 = []
        baraban_5 = []
        count = randint(10, 20)
        balance_destroyer = 0
        new_slot = [[],[],[]]

    def __str__(self):
        return self.username


class Cards(models.Model):

    mast = models.CharField(max_length=100, default='Piki')
    dostoinstvo = models.CharField(max_length=100, default='Valet')
    foto = models.ImageField(default='cards/default1.jpg', upload_to='cards')
    o4ko = models.IntegerField(default=10)

    def __str__(self):
        return self.mast+" "+self.dostoinstvo


class PTslides(models.Model):

    index_i = models.IntegerField()
    index_j = models.IntegerField()
    slide = models.ImageField( upload_to='PTslides')

    def __str__(self):
        return str(self.index_i) + " "+ str(self.index_j)


class RouletteSlides(models.Model):
    index = models.IntegerField()
    value = models.IntegerField()
    slide = models.ImageField(upload_to='RouletteSlides')

    def __str__(self):
        return str(self.index) + " " + str(self.value)


class Slots(models.Model):

    name = models.CharField(max_length=50)
    elements_image = models.ImageField(upload_to='Slot_Elements')

    def __str__(self):
        return self.name