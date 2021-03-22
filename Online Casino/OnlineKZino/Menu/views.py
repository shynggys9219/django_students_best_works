import random

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.shortcuts import render
from django.views import View
from django import forms
import Menu

from Menu.forms import CustomUserCreationForm, LoginForm, SettingsForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from Menu.models import CustomUser, Cards, PTslides, RouletteSlides, Slots

User = get_user_model()

def index(request):
    return render(request, 'Menu/index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = CustomUserCreationForm(data=request.POST)
        if user_form["username"] in CustomUser.objects.values_list("username"):

            return render(request, 'Menu/registration.html')



        if user_form.is_valid():
            user = user_form.save()

            user.save()
            if 'profile_pic' in request.FILES:
                print('found it')
                user.profile_pic = request.FILES['profile_pic']
            user.save()
            registered = True
        else:
            print(user_form.errors)
    else:

        user_form = CustomUserCreationForm()

    return render(request, 'Menu/registration.html',
                  {'user_form': user_form,

                   'registered': registered})


def user_login(request):
    user_form = LoginForm(data=request.POST)
    msg = False
    if request.method == 'POST':
        if user_form.is_valid():

            username = user_form.cleaned_data.get('username', None)
            password = user_form.cleaned_data.get('password', None)
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return HttpResponse("Your account was inactive.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username, password))
                msg = True
                return render(request, 'Menu/login.html', {'msg': msg })
    else:
        return render(request, 'Menu/login.html', {'user_form': user_form, 'msg': msg})


def TopU(request):
    users_list = CustomUser.objects.order_by('-initial_balance')

    context = {

            "users_list": users_list,

        }

    return render(request, 'Menu/top.html', context)


def Cabinet(request):

    return render(request, 'Menu/PrivateOffice.html')


def Settings(request):

    user_form = SettingsForm(data=request.POST)
    user = request.user
    if request.method == "POST":
        if request.POST.get("first_name"):
            user.first_name = request.POST.get("first_name")
        if request.POST.get("last_name"):

            user.last_name = request.POST.get("last_name")

        if request.POST.get("email"):
            user.email = request.POST.get("email")


        if 'profile_pic' in request.FILES:
            print('found it')
            user.profile_pic = request.FILES['profile_pic']
        user.save()
        return redirect("Menu/private")
    return render(request, 'Menu/settings.html', {'user_form': user_form})



def BJstart(request):
    request.user.BJboard.WJ = False
    class BjBet(forms.Form):

        bet = forms.IntegerField(min_value=100, max_value=request.user.initial_balance)

    bet_form = BjBet(data=request.POST)
    if request.method == "POST":

        if bet_form.is_valid():

            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.BJboard.bet = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            return redirect("Menu:BJ")

    cards = list(Cards.objects.all())
    shuffled = random.sample(cards, 52)
    dealer_hand = list()
    player_hand = list()

    Dcard = random.choice(shuffled)
    dealer_hand.append(Dcard)
    shuffled.remove(Dcard)
   # Dcard.o4ko = 10
    Dcard2 = random.choice(shuffled)
    dealer_hand.append(Dcard2)
    shuffled.remove(Dcard2)
    # Dcard2.o4ko = 10
    Pcard = random.choice(shuffled)
    player_hand.append(Pcard)
    shuffled.remove(Pcard)

    Pcard2 = random.choice(shuffled)
    player_hand.append(Pcard2)
    shuffled.remove(Pcard2)

    request.user.BJboard.deck = shuffled
    request.user.BJboard.dh = dealer_hand
    request.user.BJboard.ph = player_hand
    request.user.BJboard.started = True

    if Pcard.dostoinstvo == Pcard2.dostoinstvo == 'Ace':
        Pcard.dostoinstvo = 'Ace(1)'
        Pcard.o4ko = 1

    if Dcard.dostoinstvo == Dcard2.dostoinstvo == 'Ace':
        Dcard.dostoinstvo = 'Ace(1)'
        Dcard.o4ko = 1

    return render(request, 'Menu/bjSTART.html', {'dealer_hand': request.user.BJboard.dh, 'player_hand': request.user.BJboard.ph,
                'started': request.user.BJboard.started, 'bet_form' : bet_form, 'WJ': request.user.BJboard.WJ})


def BJ(request):
    P21 = 0

    for i in request.user.BJboard.ph:
        P21 += i.o4ko
    if P21 == 21:
        return redirect("Menu:BJend")
    D21 = 0

    for i in request.user.BJboard.dh:
        D21 += i.o4ko
    if P21 == 21:
        return redirect("Menu:BJend")


    if request.method == 'POST' and 'run_script' in request.POST:
        request.user.BJboard.banDD = True
        if not request.user.BJboard.dd:
            card = random.choice(request.user.BJboard.deck)
            request.user.BJboard.ph.append(card)
            request.user.BJboard.deck.remove(card)

            Po4ki = 0

            for i in request.user.BJboard.ph:
                Po4ki += i.o4ko

            if Po4ki > 21:
                key = 0
                for j in request.user.BJboard.ph:
                    if j.dostoinstvo == "Ace":
                        j.o4ko = 1
                        key = 1
                        j.dostoinstvo = 'Ace(1)'
                        Po4ki -= 10

                        break
                if key == 0:
                    return redirect("Menu:BJend")
            if Po4ki == 21:

                return redirect("Menu:BJend")


            # end game
            print(request.user.BJboard.ph)
            print(request.user.BJboard.dh)
        else:

            request.user.BJboard.dd = False
            card = random.choice(request.user.BJboard.deck)
            request.user.BJboard.ph.append(card)
            request.user.BJboard.deck.remove(card)

            Po4ki = 0

            for i in request.user.BJboard.ph:
                Po4ki += i.o4ko

            if Po4ki > 21:
                key = 0
                for j in request.user.BJboard.ph:
                    if j.dostoinstvo == "Ace":
                        j.o4ko = 1
                        key = 1
                        j.dostoinstvo = 'Ace(1)'
                        break
                if key == 0:
                    return redirect("Menu:BJend")
            return redirect("Menu:BJend")



    if request.method == 'POST' and 'stand' in request.POST:
        request.user.BJboard.dd = False
        return redirect("Menu:BJend")

    if request.method == 'POST' and 'dd' in request.POST:
        user = request.user
        user.initial_balance = user.initial_balance - request.user.BJboard.bet
        request.user.BJboard.bet = request.user.BJboard.bet * 2
        user.save()

        request.user.BJboard.dd = True


    cont = {'dealer_hand': request.user.BJboard.dh, 'player_hand': request.user.BJboard.ph,
            'started': request.user.BJboard.started, 'dd' : request.user.BJboard.dd,'bandd' : request.user.BJboard.banDD, 'WJ': request.user.BJboard.WJ}
    return render(request, 'Menu/bj.html', cont)



def BJend(request):
    request.user.BJboard.dd = False
    request.user.BJboard.banDD = False
    cont = {'started': request.user.BJboard.started}
    if request.user.BJboard.started:
          msg = str()
          DHAND = request.user.BJboard.dh
          PHAND = request.user.BJboard.ph


          Po4ki = 0
          for i in request.user.BJboard.ph:
              Po4ki += i.o4ko
          Do4ki = 0
          for i in request.user.BJboard.dh:
              Do4ki += i.o4ko

#####################___ARTIFICIAL INTELLIGENCE!!!!____CAUTION!!!!___########################
          if not request.user.BJboard.WJ:
              BotPoints = 0
              pravo_na_oshibku = 3
              if request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                  pravo_na_oshibku = 8
              elif request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 40:
                  pravo_na_oshibku = 7
              elif request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 30:
                  pravo_na_oshibku = 6
              elif request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                  pravo_na_oshibku = 5
              elif request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 10:
                  pravo_na_oshibku = 4

              print("PRAVO" ,pravo_na_oshibku)


              if Po4ki <= 21:

                    for i in request.user.BJboard.dh:
                        BotPoints += i.o4ko
                    while BotPoints <= 10:
                        card = random.choice(request.user.BJboard.deck)
                        request.user.BJboard.dh.append(card)
                        request.user.BJboard.deck.remove(card)
                        BotPoints += card.o4ko





                    if BotPoints == 14:
                        if request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 == 100:
                            chance = random.randint(1, 9)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                        else:
                            chance = random.randint(1, 15)

                        if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                            print("proizoshel trolling(7)")

                            for f in request.user.BJboard.deck:
                                if f.dostoinstvo == '7':
                                    card = f

                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    BotPoints += card.o4ko
                                    break


                    if BotPoints == 15:
                        if request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 == 100:
                            chance = random.randint(1, 9)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                        else:
                            chance = random.randint(1, 15)

                        if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                            print("proizoshel trolling(6)")

                            for f in request.user.BJboard.deck:
                                if f.dostoinstvo == '6':
                                    card = f

                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    BotPoints += card.o4ko
                                    break

                    if BotPoints == 16:
                        if request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 == 100:
                            chance = random.randint(1, 9)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                        else:
                            chance = random.randint(1, 15)
                        if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                            print("proizoshel trolling(5)")

                            for f in request.user.BJboard.deck:
                                if f.dostoinstvo == '5':
                                    card = f

                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    BotPoints += card.o4ko
                                    break

                    if BotPoints == 17:
                        if request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 == 100:
                            chance = random.randint(1, 9)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                        else:
                            chance = random.randint(1, 15)

                        if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                            print("proizoshel trolling(4)")

                            for f in request.user.BJboard.deck:
                                if f.dostoinstvo == '4':
                                    card = f

                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    BotPoints += card.o4ko
                                    break

                    if BotPoints == 18:
                        if request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 == 100:
                            chance = random.randint(1, 9)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                        else:
                            chance = random.randint(1, 15)

                        if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                            print("proizoshel trolling(3)")

                            for f in request.user.BJboard.deck:
                                if f.dostoinstvo == '3':
                                    card = f

                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    BotPoints += card.o4ko
                                    break


                    if BotPoints == 19:
                        if request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 == 100:
                            chance = random.randint(1, 9)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                        elif request.user.BJboard.bet / (
                                request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                        else:
                            chance = random.randint(1, 15)

                        if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                            print("proizoshel trolling(2)")

                            for f in request.user.BJboard.deck:
                                if f.dostoinstvo == '2':
                                    card = f

                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    BotPoints += card.o4ko
                                    break


                    if BotPoints == 20:
                       if request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet)  * 100 == 100:
                            chance = random.randint(1, 9)
                       elif request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 50:
                            chance = random.randint(1, 11)
                       elif request.user.BJboard.bet / (request.user.initial_balance + request.user.BJboard.bet) * 100 > 20:
                            chance = random.randint(1, 13)
                       else:
                            chance = random.randint(1, 15)

                       if chance == 1 or chance == 2 or chance == 3 or chance == 4:

                           print("proizoshel trolling(ace)")

                           for f in request.user.BJboard.deck:
                               if f.dostoinstvo == 'Ace':
                                   card = f
                                   card.o4ko = 1
                                   card.dostoinstvo = "Ace(1)"
                                   request.user.BJboard.dh.append(card)
                                   request.user.BJboard.deck.remove(card)
                                   BotPoints += card.o4ko
                                   break



                    while Po4ki >= BotPoints:

                        if BotPoints == 21:
                            break
                        if Po4ki == BotPoints == 21:
                            break

                        if BotPoints == Po4ki:
                            chance = random.randint(1, 2)
                            if chance == 1:
                                print("Bot  risknul")
                                card = random.choice(request.user.BJboard.deck)
                                request.user.BJboard.dh.append(card)
                                request.user.BJboard.deck.remove(card)
                                Do4ki += card.o4ko
                                if Do4ki > 21:

                                    for j in request.user.BJboard.dh:
                                        if j.dostoinstvo == "Ace":
                                            j.o4ko = 1
                                            Do4ki -= 10
                                            j.dostoinstvo = 'Ace(1)'
                                            break
                                break
                            else:
                                print("Bot ne risknul")
                                break

                        card = random.choice(request.user.BJboard.deck)

                        BotPoints += card.o4ko
                        if BotPoints > 21:

                            for j in request.user.BJboard.dh:
                                if j.dostoinstvo == "Ace":
                                    j.o4ko = 1
                                    BotPoints -= 10
                                    j.dostoinstvo = 'Ace(1)'
                                    break

                            if BotPoints > 21:
                                 if pravo_na_oshibku > 0:
                                    BotPoints -= card.o4ko
                                    print("Bot made a mistake))")
                                    pravo_na_oshibku -= 1
                                    continue
                                 else:
                                    request.user.BJboard.dh.append(card)
                                    request.user.BJboard.deck.remove(card)
                                    break
                        request.user.BJboard.dh.append(card)
                        request.user.BJboard.deck.remove(card)




          elif request.user.BJboard.WJ:

                while(Po4ki >= Do4ki and Do4ki<=21 and Po4ki <=21):
                    if Po4ki == Do4ki == 21:
                        break
                    if Do4ki == Po4ki:
                        chance = random.randint(1, 2)
                        if chance == 1:
                            print("Bot  risknul")
                            card = random.choice(request.user.BJboard.deck)
                            request.user.BJboard.dh.append(card)
                            request.user.BJboard.deck.remove(card)
                            Do4ki += card.o4ko
                            if Do4ki > 21:

                                for j in request.user.BJboard.dh:
                                    if j.dostoinstvo == "Ace":
                                        j.o4ko = 1
                                        Do4ki -= 10
                                        j.dostoinstvo = 'Ace(1)'
                                        break
                            break
                        else:
                            print("Bot ne risknul")
                            break




                    card = random.choice(request.user.BJboard.deck)
                    request.user.BJboard.dh.append(card)
                    request.user.BJboard.deck.remove(card)
                    Do4ki += card.o4ko
                    if Do4ki > 21:

                        for j in request.user.BJboard.dh:
                                if j.dostoinstvo == "Ace":
                                    j.o4ko = 1
                                    Do4ki -= 10
                                    j.dostoinstvo = 'Ace(1)'
                                    break




##############################################################################$$##############


          Do4ki = 0
          for i in request.user.BJboard.dh:
              Do4ki += i.o4ko



          if Po4ki > 21 or Do4ki > 21:
              if Po4ki > 21:
                 print(request.user.BJboard.ph)
                 print(request.user.BJboard.dh)
                 print(Po4ki)
                 request.user.BJboard.dh = list()
                 request.user.BJboard.ph = list()
                 request.user.BJboard.counter = 2
                 request.user.BJboard.deck = list()
                 request.user.BJboard.started = False
                 request.user.BJboard.bet = int()
                 msg = "You lost! More then 21 points! " + "Dealer's points: " + str(Do4ki) + "  Your points: " + str(Po4ki)
              elif Do4ki > 21:
                  print(request.user.BJboard.ph)
                  print(request.user.BJboard.dh)
                  print(Po4ki)
                  print(Do4ki)
                  request.user.BJboard.dh = list()
                  request.user.BJboard.ph = list()
                  request.user.BJboard.counter = 2
                  request.user.BJboard.deck = list()
                  request.user.BJboard.started = False

                  # WON BET
                  bet = request.user.BJboard.bet * 2
                  user = request.user
                  user.initial_balance = user.initial_balance + bet
                  user.save()

                  request.user.BJboard.bet = int()

                  msg = "You won! Dealer have more then 21!" + "Dealer's points: " + str(
                      Do4ki) + "  Your points: " + str(Po4ki)




          elif Po4ki > Do4ki:
              print(request.user.BJboard.ph)
              print(request.user.BJboard.dh)
              print(Po4ki)
              print(Do4ki)
              request.user.BJboard.dh = list()
              request.user.BJboard.ph = list()
              request.user.BJboard.counter = 2
              request.user.BJboard.deck = list()
              request.user.BJboard.started = False

              # WON BET
              bet = request.user.BJboard.bet * 2
              user = request.user
              user.initial_balance = user.initial_balance + bet
              user.save()

              request.user.BJboard.bet = int()

              msg = "You won!" + "Dealer's points: " + str(Do4ki) +"  Your points: " +str(Po4ki)
          elif Po4ki < Do4ki:
              print(request.user.BJboard.ph)
              print(request.user.BJboard.dh)
              print(Po4ki)
              print(Do4ki)
              request.user.BJboard.dh = list()
              request.user.BJboard.ph = list()
              request.user.BJboard.counter = 2
              request.user.BJboard.deck = list()
              request.user.BJboard.started = False
              request.user.BJboard.bet = int()
              msg = "You lost!" + "Dealer's points: " + str(Do4ki) + "  Your points: " + str(Po4ki)

          elif Po4ki == Do4ki:
              print(request.user.BJboard.ph)
              print(request.user.BJboard.dh)
              print(Po4ki)
              print(Do4ki)
              request.user.BJboard.dh = list()
              request.user.BJboard.ph = list()
              request.user.BJboard.counter = 2
              request.user.BJboard.deck = list()
              request.user.BJboard.started = False
              # DRAW BET
              bet = request.user.BJboard.bet
              user = request.user
              user.initial_balance = user.initial_balance + bet
              user.save()

              request.user.BJboard.bet = int()
              msg = "Draw!" + "Dealer's points: " + str(Do4ki) +"  Your points: " +str(Po4ki)

          cont = {'dealer_hand': DHAND, 'player_hand': PHAND,
                  'started': True, 'msg': msg, 'WJ': request.user.BJboard.WJ}


    return render(request, 'Menu/bjEND.html', cont)









def WJstart(request):

    class BjBet(forms.Form):

        bet = forms.IntegerField(min_value=100, max_value=request.user.initial_balance/100*20)

    bet_form = BjBet(data=request.POST)
    if request.method == "POST":

        if bet_form.is_valid():

            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.BJboard.bet = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            return redirect("Menu:BJ")

    cards = list(Cards.objects.all())
    shuffled = random.sample(cards, 52)
    dealer_hand = list()
    player_hand = list()

    Dcard = random.choice(shuffled)
    dealer_hand.append(Dcard)
    shuffled.remove(Dcard)
   # Dcard.o4ko = 10
    Dcard2 = random.choice(shuffled)
    dealer_hand.append(Dcard2)
    shuffled.remove(Dcard2)
    # Dcard2.o4ko = 10
    Pcard = random.choice(shuffled)
    player_hand.append(Pcard)
    shuffled.remove(Pcard)

    Pcard2 = random.choice(shuffled)
    player_hand.append(Pcard2)
    shuffled.remove(Pcard2)

    request.user.BJboard.deck = shuffled
    request.user.BJboard.dh = dealer_hand
    request.user.BJboard.ph = player_hand
    request.user.BJboard.WJ = True

    request.user.BJboard.started = True

    if Pcard.dostoinstvo == Pcard2.dostoinstvo == 'Ace':
        Pcard.dostoinstvo = 'Ace(1)'
        Pcard.o4ko = 1

    if Dcard.dostoinstvo == Dcard2.dostoinstvo == 'Ace':
        Dcard.dostoinstvo = 'Ace(1)'
        Dcard.o4ko = 1

    return render(request, 'Menu/bjSTART.html', {'dealer_hand': request.user.BJboard.dh, 'player_hand': request.user.BJboard.ph,
                'started': request.user.BJboard.started, 'bet_form' : bet_form, 'WJ': request.user.BJboard.WJ})


def PTstart(request):

    if request.method == "POST":
        return redirect("Menu:PT")
    return render(request, 'Menu/ptSTART.html', {'tries': int(request.user.initial_balance/2000)})


def PT(request):
    index_i = 0
    index_j = 0
    a = [
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    ]
    b = 99
    if request.method == "POST" and 'st11' in request.POST:
        user = request.user
        request.user.PT.finished = False
        if user.initial_balance > 2000:

            user.initial_balance = user.initial_balance - 2000
            user.save()
            request.user.PT.started = True
        else:
            request.user.PT.started = False
            return redirect("Menu:Cabinet")

        index_i = 0
        index_j = 1
        b = 11
        a[0][1] = b
        print(11)
        request.user.PT.indexes_i = list()
        request.user.PT.indexes_j = list()
        request.user.PT.slideshow = list()
        request.user.PT.started = True

    if request.method == "POST" and 'st22' in request.POST:
        user = request.user
        request.user.PT.finished = False
        if user.initial_balance > 2000:

            user.initial_balance = user.initial_balance - 2000
            user.save()
            request.user.PT.started = True
        else:
            request.user.PT.started = False
            return redirect("Menu:Cabinet")
        index_i = 0
        index_j = 3
        b = 22
        a[0][3] = b
        print(22)
        request.user.PT.indexes_i = list()
        request.user.PT.indexes_j = list()
        request.user.PT.slideshow = list()
        request.user.PT.started = True
    if request.method == "POST" and 'st33' in request.POST:
        user = request.user
        request.user.PT.finished = False
        if user.initial_balance > 2000:

            user.initial_balance = user.initial_balance - 2000
            user.save()
            request.user.PT.started = True
        else:
            request.user.PT.started = False
            return redirect("Menu:Cabinet")
        index_i = 0
        index_j = 5
        b = 33
        a[0][5] = b
        print(33)
        request.user.PT.indexes_i = list()
        request.user.PT.indexes_j = list()
        request.user.PT.slideshow = list()
        request.user.PT.started = True
    if request.method == "POST" and 'st44' in request.POST:
        user = request.user
        request.user.PT.finished = False
        if user.initial_balance > 2000:

            user.initial_balance = user.initial_balance - 2000
            user.save()
            request.user.PT.started = True
        else:
            request.user.PT.started = False
            return redirect("Menu:Cabinet")
        index_i = 0
        index_j = 7
        b = 44
        a[0][7] = b
        print(44)
        request.user.PT.indexes_i = list()
        request.user.PT.indexes_j = list()
        request.user.PT.slideshow = list()
        request.user.PT.started = True
    if request.method == "POST" and 'st55' in request.POST:
        user = request.user
        request.user.PT.finished = False
        if user.initial_balance > 2000:

            user.initial_balance = user.initial_balance - 2000
            user.save()
            request.user.PT.started = True
        else:
            request.user.PT.started = False
            return redirect("Menu:Cabinet")
        index_i = 0
        index_j = 9
        b = 55
        a[0][9] = b
        print(55)
        request.user.PT.indexes_i = list()
        request.user.PT.indexes_j = list()
        request.user.PT.slideshow = list()
        request.user.PT.started = True
    if request.method == "POST" and 'st66' in request.POST:
        user = request.user
        request.user.PT.finished = False
        if user.initial_balance > 2000:

            user.initial_balance = user.initial_balance - 2000
            user.save()
            request.user.PT.started = True
        else:
            request.user.PT.started = False
            return redirect("Menu:Cabinet")
        print(66)
        b = 66
        index_i = 0
        index_j = 11
        a[0][11] = b
        request.user.PT.indexes_i = list()
        request.user.PT.indexes_j = list()
        request.user.PT.slideshow = list()
        request.user.PT.started = True
    if request.user.PT.started:
        for i in range(15):
            print(index_i , index_j)
            request.user.PT.indexes_i.append(index_i)
            request.user.PT.indexes_j.append(index_j)
            if a[14][5] == b:
                c = random.randint(0, 100)
                if 0 <= c < 10:  # c >= 0 and c < 10
                    a[index_i + 1][index_j + 1] = b
                    index_j += 1
                    index_i +=1
                    print("You won main prize - 24000!!")

                    print(c)
                    continue
                elif 10 <= c < 100:
                    a[index_i + 1][index_j - 1] = b
                    index_j -= 1
                    index_i += 1
                    print("You won 1000!")

                    print(c)
                    continue
            elif a[14][7] == b:
                c = random.randint(0, 100)
                if 0 <= c < 10:
                    a[index_i + 1][index_j - 1] = b
                    index_j -= 1
                    index_i += 1
                    print("You won main prize - 24000!!")

                    print(c)
                    continue
                elif 10 <= c < 100:
                    a[index_i + 1][index_j + 1] = b
                    index_j += 1
                    index_i += 1
                    print("You won 500!")

                    print(c)
                    continue
            elif a[14][9] == b:
                c = random.randint(0, 9)
                if 0 <= c < 2:  # c >= 0 and c < 10
                    a[index_i + 1][index_j + 1] = b
                    index_j += 1
                    index_i += 1
                    print("You won 6k!!")

                    print(c)
                    continue
                else:
                    a[index_i + 1][index_j - 1] = b
                    index_j -= 1
                    index_i += 1
                    print("You won 750!")

                    print(c)
                    continue
            elif a[14][11] == b:
                c = random.randint(0, 9)
                if 0 <= c < 2:
                    a[index_i + 1][index_j - 1] = b
                    index_j -= 1
                    index_i += 1
                    print("You won6к!")

                    print(c)
                    continue
                else:
                    a[index_i + 1][index_j + 1] = b
                    index_j += 1
                    index_i += 1
                    print("You won 100!")

                    print(c)
                    continue
            if index_i == i and index_j == 0 and a[i][0] != 0:
                a[index_i + 1][index_j + 1] = b
                index_i += 1
                index_j += 1
                continue
            elif index_i == i and index_j == 12 and a[i][12] != 0:
                a[index_i + 1][index_j - 1] = b
                index_i += 1
                index_j -= 1
                continue
            c = (random.randint(0, 1))
            if c == 0:
                a[index_i + 1][index_j - 1] = b
                index_i += 1
                index_j -= 1
            elif c == 1:
                a[index_i + 1][index_j + 1] = b
                index_i += 1
                index_j += 1
        print(index_i, index_j)
        request.user.PT.indexes_i.append(index_i)
        request.user.PT.indexes_j.append(index_j)

        request.user.PT.started = False
        for i in range(16):
            print(a[i])
        return redirect("Menu:PTend")
    return render(request, 'Menu/pt.html', {'tries': int(request.user.initial_balance/2000)})

def PTend(request):
    slides = list()
    print("PTend")
    slides = request.user.PT.slideshow
    print(request.user.PT.indexes_i)
    print(request.user.PT.indexes_j)
    if request.user.PT.finished == False:
        if request.user.PT.indexes_i and request.user.PT.indexes_j:
             for i in range(16):


                 slide = PTslides.objects.get(index_i = request.user.PT.indexes_i[i], index_j = request.user.PT.indexes_j[i])
                 request.user.PT.slideshow.append(slide)

             if request.user.PT.indexes_j[15]==0:
                 slide = PTslides.objects.get(index_i=16, index_j=150)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 500
                 user.save()


             if request.user.PT.indexes_j[15]==2:
                 slide = PTslides.objects.get(index_i=16, index_j=152)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 3000
                 user.save()


             if request.user.PT.indexes_j[15]==4:
                 slide = PTslides.objects.get(index_i=16, index_j=154)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 1000
                 user.save()

             if request.user.PT.indexes_j[15]==6:
                 slide = PTslides.objects.get(index_i=16, index_j=156)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 24000
                 user.save()

             if request.user.PT.indexes_j[15]==8:
                 slide = PTslides.objects.get(index_i=16, index_j=158)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 750
                 user.save()

             if request.user.PT.indexes_j[15]==10:
                 slide = PTslides.objects.get(index_i=16, index_j=1510)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 6000
                 user.save()

             if request.user.PT.indexes_j[15]==12:
                 slide = PTslides.objects.get(index_i=16, index_j=1512)
                 request.user.PT.slideshow.append(slide)
                 user = request.user
                 user.initial_balance = user.initial_balance + 100
                 user.save()


             print(request.user.PT.slideshow)

             slides = request.user.PT.slideshow
        request.user.PT.finished = True


    if request.method == "POST" and  'TA' in request.POST:
        return redirect("Menu:PT")
    return render(request, 'Menu/ptEND.html', {'slideshow': slides})


def RouletteStart(request):
    class RouletteBet(forms.Form):
        bet = forms.IntegerField(min_value=1000, max_value=request.user.initial_balance)

    bet_form = RouletteBet(data=request.POST)
    if request.method == "POST" and 'runRoulette' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            request.user.Roulette.bet = bet
            return redirect("Menu:Roulette")

    return render(request, 'Menu/RouletteSTART.html', {'bet_form': bet_form})


def Roulette(request):
    bet = request.user.Roulette.bet
    message = "Your bet: " + str(bet) + \
              ". Your balance: " + str(request.user.initial_balance) + "points."

    # bet for every field from 0 to 36
    for i in range(0, 37):
        if request.method == "POST" and str(i) in request.POST:
            user = request.user
            request.user.Roulette.finished = False

            if request.user.initial_balance >= bet:
                user.initial_balance = user.initial_balance - bet
                user.Roulette.fields[i] += bet
                request.user.Roulette.all_bets += bet
                user.save()
                message = "You bet on field '" + str(i) + "' " + str(request.user.Roulette.fields[i]) +\
                          " .Your balance: " + str(request.user.initial_balance) + "points."
                request.user.Roulette.started = True

            else:
                request.user.Roulette.started = False
                message = "You don't have enough money."

    # bet for three part
    # (1 - 12)
    if request.method == "POST" and '1st' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.threePart[1] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '1st 12' " + str(request.user.Roulette.threePart[1]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # (13 - 24)
    if request.method == "POST" and '2nd' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.threePart[2] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '2nd 12' " + str(request.user.Roulette.threePart[2]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # (25 - 36)
    if request.method == "POST" and '3rd' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.threePart[3] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '3rd 12' " + str(request.user.Roulette.threePart[3]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # bet for small/large
    # (1-18)
    if request.method == "POST" and '1-18' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.twoPart[1] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '1-18' " + str(request.user.Roulette.twoPart[1]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # (19-36)
    if request.method == "POST" and '19-36' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.twoPart[2] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '19-36' " + str(request.user.Roulette.twoPart[2]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # bet for colors
    # red
    if request.method == "POST" and 'red' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.color[1] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field 'RED' " + str(request.user.Roulette.color[1]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # black
    if request.method == "POST" and 'black' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.color[2] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field 'BLACK' " + str(request.user.Roulette.color[2]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # bet for parity
    # even
    if request.method == "POST" and 'even' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.parity[1] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field 'EVEN' " + str(request.user.Roulette.parity[1]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # odd
    if request.method == "POST" and 'odd' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.parity[2] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field 'ODD' " + str(request.user.Roulette.parity[2]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # bet for rows
    # (1 - 34)
    if request.method == "POST" and '1-34' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.row[1] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '1-34' " + str(request.user.Roulette.row[1]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # (2 - 35)
    if request.method == "POST" and '2-35' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.row[2] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '2-35' " + str(request.user.Roulette.row[2]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    # (3 - 36)
    if request.method == "POST" and '3-36' in request.POST:
        user = request.user
        request.user.Roulette.finished = False

        if request.user.initial_balance >= request.user.Roulette.bet:
            user.initial_balance = user.initial_balance - user.Roulette.bet
            user.Roulette.row[3] += user.Roulette.bet
            request.user.Roulette.all_bets += user.Roulette.bet
            user.save()
            message = "You bet on field '3-36' " + str(request.user.Roulette.row[3]) + \
                      " .Your balance: " + str(request.user.initial_balance) + "points."
            request.user.Roulette.started = True

        else:
            request.user.Roulette.started = False
            message = "You don't have enough money."

    if request.method == "POST" and 'clear' in request.POST:
        request.user.Roulette.started = False
        user = request.user
        user.initial_balance += request.user.Roulette.all_bets
        request.user.Roulette.all_bets = 0
        user.save()

        request.user.Roulette.fields = dict.fromkeys([i for i in range(37)], 0)
        request.user.Roulette.threePart = dict.fromkeys([1, 2, 3], 0)
        request.user.Roulette.twoPart = dict.fromkeys([1, 2], 0)
        request.user.Roulette.color = dict.fromkeys([1, 2], 0)
        request.user.Roulette.parity = dict.fromkeys([1, 2], 0)
        request.user.Roulette.row = dict.fromkeys([1, 2, 3], 0)

        message = "All your bets are cleaned."

    if request.method == "POST" and 'double' in request.POST:
        if request.user.Roulette.all_bets * 2 <= request.user.initial_balance:
            user = request.user
            user.initial_balance -= request.user.Roulette.all_bets
            user.save()
            request.user.Roulette.all_bets += request.user.Roulette.all_bets

            for i in range(0, 37):
                request.user.Roulette.fields[i] += request.user.Roulette.fields[i]
            for i in range(1, 4):
                request.user.Roulette.threePart[i] += request.user.Roulette.threePart[i]
            for i in range(1, 3):
                request.user.Roulette.twoPart[i] += request.user.Roulette.twoPart[i]
            for i in range(1, 3):
                request.user.Roulette.color[i] += request.user.Roulette.color[i]
            for i in range(1, 3):
                request.user.Roulette.parity[i] += request.user.Roulette.parity[i]
            for i in range(1, 4):
                request.user.Roulette.row[i] += request.user.Roulette.row[i]

            message = "All your bets are doubled."
        else:
            message = "You don't have enough points."

    if request.method == "POST" and 'spin' in request.POST:
        request.user.Roulette.finished = False
        if request.user.Roulette.started:
            red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            balance = 0
            ans = random.randint(0, 37)
            request.user.Roulette.index = ans
            print("+++++++++++++++++++", ans, "++++++++++++++++")

            # fields
            for i in range(0, 37):
                if ans == i:
                    balance += request.user.Roulette.fields[i] * 36

            # parity
            if ans % 2 == 0:
                balance += request.user.Roulette.parity[1] * 2
            if ans % 2 == 1:
                balance += request.user.Roulette.parity[2] * 2

            # color
            if ans in red:
                balance += request.user.Roulette.color[1] * 2
            if ans in black:
                balance += request.user.Roulette.color[2] * 2

            # rows
            if ans in range(1, 35, 3):
                balance += request.user.Roulette.row[1] * 3
            if ans in range(2, 36, 3):
                balance += request.user.Roulette.row[2] * 3
            if ans in range(3, 37, 3):
                balance += request.user.Roulette.row[3] * 3

            # dozens
            if ans in range(1, 13):
                balance += request.user.Roulette.threePart[1] * 3
            if ans in range(13, 25):
                balance += request.user.Roulette.threePart[2] * 3
            if ans in range(25, 37):
                balance += request.user.Roulette.threePart[3] * 3

            # small / large
            if ans in range(1, 19):
                balance += request.user.Roulette.twoPart[1] * 2
            if ans in range(19, 37):
                balance += request.user.Roulette.twoPart[2] * 2

            request.user.Roulette.fields = dict.fromkeys([i for i in range(37)], 0)
            request.user.Roulette.threePart = dict.fromkeys([1, 2, 3], 0)
            request.user.Roulette.twoPart = dict.fromkeys([1, 2], 0)
            request.user.Roulette.color = dict.fromkeys([1, 2], 0)
            request.user.Roulette.parity = dict.fromkeys([1, 2], 0)
            request.user.Roulette.row = dict.fromkeys([1, 2, 3], 0)
            request.user.Roulette.slideshow = list()
            request.user.Roulette.all_bets = 0

            if balance <= 0:
                message = "Better luck next time!"
            else:
                message = "You won " + str(balance) + " points."

            user = request.user
            user.initial_balance += balance
            user.save()

            request.user.Roulette.started = False
            request.user.Roulette.message = message
            return redirect("Menu:RouletteEnd")

        else:
            message = "You haven't bet on any field."
            redirect("Menu:Roulette")

    return render(request, 'Menu/Roulette.html', {'message': message})


def RouletteEnd(request):
    slides = list()
    roulette = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
                5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
    start = roulette.index(request.user.Roulette.index)
    print("value:", request.user.Roulette.index, "index", start)
    if not request.user.Roulette.finished:
        for i in range(len(roulette)):
            slide = RouletteSlides.objects.get(value=roulette[start])
            request.user.Roulette.slideshow.append(slide)

            if start == 36:
                start = -1
            start += 1

        slides = request.user.Roulette.slideshow
        request.user.Roulette.finished = True

    if request.method == "POST" and 'TA' in request.POST:
        return redirect("Menu:Roulette")
    return render(request, 'Menu/RouletteEND.html', {'slideshow': slides})


def begaSTART1(request):
    if request.method == "POST":
        return redirect("Menu:begaSTART")

    return render(request, 'Menu/BegaStart1.html', )


def begaSTART(request):
    class BjBet1(forms.Form):

        bet = forms.IntegerField(min_value=100, max_value=request.user.initial_balance)

    bet_form = BjBet1(data=request.POST)

    if request.method == "POST" and 'bet1' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.bet1 = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")

    if request.method == "POST" and 'bet2' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.bet2 = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")

    if request.method == "POST" and 'bet3' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.bet3 = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")
    if request.method == "POST" and 'bet4' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.bet4 = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")
    if request.method == "POST" and 'bet5' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.bet5 = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")
    if request.method == "POST" and 'betAD' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.betALLDIE = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")
    if request.method == "POST" and 'betAA' in request.POST:

        if bet_form.is_valid():
            bet = int(request.POST.get('bet'))
            print("ur bet", bet)
            request.user.Ska4ki.betALLALIVE = bet
            user = request.user
            user.initial_balance = user.initial_balance - bet
            user.save()
            request.user.Ska4ki.started = True
            return redirect("Menu:bega")

    return render(request, 'Menu/BegaStart.html', {'bet_form': bet_form})


def bega(request):
    if request.method == "POST":
        return redirect("Menu:begaSTART")
    if request.user.Ska4ki.started:

        winner1 = 0
        winner2 = 0
        winner3 = 0
        winner4 = 0
        winner5 = 0
        death_distance1 = 1200
        speed1 = random.randint(50, 300)
        death_chance1 = random.randint(1, 3)
        if death_chance1 == 1:
            print("smert1")
            death_distance1 = random.randint(1, 999)
            print(death_distance1)

        death_distance2 = 1200
        speed2 = random.randint(50, 300)
        death_chance2 = random.randint(1, 3)
        if death_chance2 == 1:
            print("smert2")
            death_distance2 = random.randint(1, 999)
            print(death_distance2)

        death_distance3 = 1200
        speed3 = random.randint(50, 300)
        death_chance3 = random.randint(1, 3)
        if death_chance3 == 1:
            print("smert3")
            death_distance3 = random.randint(1, 999)
            print(death_distance3)

        death_distance4 = 1200
        speed4 = random.randint(50, 300)
        death_chance4 = random.randint(1, 3)
        if death_chance4 == 1:
            print("smert4")
            death_distance4 = random.randint(1, 999)
            print(death_distance4)

        death_distance5 = 1200
        speed5 = random.randint(50, 300)
        death_chance5 = random.randint(1, 3)
        if death_chance5 == 1:
            print("smert5")
            death_distance5 = random.randint(1, 999)
            print(death_distance5)
        speeds = list()
        if death_chance1 != 1:
            speeds.append(speed1)
        if death_chance2 != 1:
            speeds.append(speed2)
        if death_chance3 != 1:
            speeds.append(speed3)
        if death_chance4 != 1:
            speeds.append(speed4)
        if death_chance5 != 1:
            speeds.append(speed5)

        if (min(speeds) == speed1):
            winner1 = 1
        if (min(speeds) == speed2):
            winner2 = 1
        if (min(speeds) == speed3):
            winner3 = 1
        if (min(speeds) == speed4):
            winner4 = 1
        if (min(speeds) == speed5):
            winner5 = 1

        if request.user.Ska4ki.bet1:
            if winner1 == 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.bet1 * 5
                user.save()

            request.user.Ska4ki.bet1 = int()

        if request.user.Ska4ki.bet2:
            if winner2 == 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.bet2 * 5
                user.save()

            request.user.Ska4ki.bet2 = int()
        if request.user.Ska4ki.bet3:
            if winner3 == 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.bet3 * 5
                user.save()

            request.user.Ska4ki.bet3 = int()

        if request.user.Ska4ki.bet4:
            if winner4 == 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.bet4 * 5
                user.save()

            request.user.Ska4ki.bet4 = int()

        if request.user.Ska4ki.bet5:
            if winner5 == 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.bet5 * 5
                user.save()

            request.user.Ska4ki.bet5 = int()

        if request.user.Ska4ki.betALLDIE:
            if death_chance1 == 1 and death_chance2 == 1 and death_chance3 == 1 and death_chance4 == 1 and death_chance5 == 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.betALLDIE * 10
                user.save()

            request.user.Ska4ki.betALLDIE = int()

        if request.user.Ska4ki.betALLALIVE:
            if death_chance1 != 1 and death_chance2 != 1 and death_chance3 != 1 and death_chance4 != 1 and death_chance5 != 1:
                user = request.user
                user.initial_balance = user.initial_balance + request.user.Ska4ki.betALLALIVE * 2
                user.save()

            request.user.Ska4ki.betALLALIVE = int()
        request.user.Ska4ki.started = False

    else:
        winner1 = 0
        winner2 = 0
        winner3 = 0
        winner4 = 0
        winner5 = 0
        death_distance1 = 0
        death_distance2 = 0
        death_distance3 = 0
        death_distance4 = 0
        death_distance5 = 0
        death_chance1 = 0
        death_chance2 = 0
        death_chance3 = 0
        death_chance4 = 0
        death_chance5 = 0
        speed1 = 0
        speed2 = 0
        speed3 = 0
        speed4 = 0
        speed5 = 0


    return render(request, 'Menu/Bega.html',
                  {'speed1': speed1, 'death_chance1': death_chance1, 'death_distance1': death_distance1,
                   'speed2': speed2, 'death_chance2': death_chance2,
                   'death_distance2': death_distance2,
                   'speed3': speed3, 'death_chance3': death_chance3,
                   'death_distance3': death_distance3,
                   'speed4': speed4, 'death_chance4': death_chance4,
                   'death_distance4': death_distance4, 'speed5': speed5, 'death_chance5': death_chance5,
                   'death_distance5': death_distance5,
                   'winner1': winner1, 'winner2': winner2, 'winner3': winner3, 'winner4': winner4, 'winner5': winner5,

                   })

def Slot_Machine_Start(request):
    if request.method == "POST":
        elements = ["ZW", "KC", "ES", "SP", "KQ", "The Hand", "GE"]

        baraban_1 = []
        baraban_2 = []
        baraban_3 = []
        baraban_4 = []
        baraban_5 = []

        for i in range(1000):
            c = random.randint(0, 100)
            if c > 94:
                baraban_1.append(elements[-1])
            else:
                c = random.randint(0, 5)
                baraban_1.append(elements[c])

        for i in range(1000):
            c = random.randint(0, 100)
            if c > 94:
                baraban_2.append(elements[-1])
            else:
                c = random.randint(0, 5)
                baraban_2.append(elements[c])

        for i in range(1000):
            c = random.randint(0, 100)
            if c > 94:
                baraban_3.append(elements[-1])
            else:
                c = random.randint(0, 5)
                baraban_3.append(elements[c])

        for i in range(1000):
            c = random.randint(0, 100)
            if c > 94:
                baraban_4.append(elements[-1])
            else:
                c = random.randint(0, 5)
                baraban_4.append(elements[c])

        for i in range(1000):
            c = random.randint(0, 100)
            if c > 94:
                baraban_5.append(elements[-1])
            else:
                c = random.randint(0, 5)
                baraban_5.append(elements[c])

        request.user.Slot.baraban_1 = baraban_1
        request.user.Slot.baraban_2 = baraban_2
        request.user.Slot.baraban_3 = baraban_3
        request.user.Slot.baraban_4 = baraban_4
        request.user.Slot.baraban_5 = baraban_5
        print(len(request.user.Slot.baraban_1))
        return redirect("Menu:Slots")

    return render(request, 'Menu/JOJO_Slots.html')


def Slot_Machine(request):

    elements = ["ZW", "KC", "ES", "SP", "KQ", "The Hand", "GE"]

    if request.method == "POST" and 'st11' in request.POST:

        stavka = 1000

        request.user.initial_balance -= stavka

        if request.user.Slot.balance_destroyer >= request.user.Slot.count:

            win_coef = 0

            slot = [[], [], []]

            bal_destr_elements = ["1", "2", "3", "V", "^", "Molnia", "ainloM"]
            c = random.randint(0, 6)

            if bal_destr_elements[c] == "1":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i])
                        slot[1].append(request.user.Slot.baraban_1[i + 1])
                        slot[2].append(request.user.Slot.baraban_1[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i])
                        slot[1].append(request.user.Slot.baraban_2[i + 1])
                        slot[2].append(request.user.Slot.baraban_2[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i])
                        slot[1].append(request.user.Slot.baraban_3[i + 1])
                        slot[2].append(request.user.Slot.baraban_3[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i])
                        slot[1].append(request.user.Slot.baraban_4[i + 1])
                        slot[2].append(request.user.Slot.baraban_4[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i])
                        slot[1].append(request.user.Slot.baraban_5[i + 1])
                        slot[2].append(request.user.Slot.baraban_5[i + 2])
                        break

            elif bal_destr_elements[c] == "2":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i - 1])
                        slot[1].append(request.user.Slot.baraban_1[i])
                        slot[2].append(request.user.Slot.baraban_1[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i - 1])
                        slot[1].append(request.user.Slot.baraban_2[i])
                        slot[2].append(request.user.Slot.baraban_2[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i - 1])
                        slot[1].append(request.user.Slot.baraban_3[i])
                        slot[2].append(request.user.Slot.baraban_3[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i - 1])
                        slot[1].append(request.user.Slot.baraban_4[i])
                        slot[2].append(request.user.Slot.baraban_4[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i - 1])
                        slot[1].append(request.user.Slot.baraban_5[i])
                        slot[2].append(request.user.Slot.baraban_5[i + 1])
                        break

            elif bal_destr_elements[c] == "3":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i - 2])
                        slot[1].append(request.user.Slot.baraban_1[i - 1])
                        slot[2].append(request.user.Slot.baraban_1[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i - 2])
                        slot[1].append(request.user.Slot.baraban_2[i - 1])
                        slot[2].append(request.user.Slot.baraban_2[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i - 2])
                        slot[1].append(request.user.Slot.baraban_3[i - 1])
                        slot[2].append(request.user.Slot.baraban_3[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i - 2])
                        slot[1].append(request.user.Slot.baraban_4[i - 1])
                        slot[2].append(request.user.Slot.baraban_4[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i - 2])
                        slot[1].append(request.user.Slot.baraban_5[i - 1])
                        slot[2].append(request.user.Slot.baraban_5[i])
                        break

            elif bal_destr_elements[c] == "V":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i])
                        slot[1].append(request.user.Slot.baraban_1[i + 1])
                        slot[2].append(request.user.Slot.baraban_1[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i - 1])
                        slot[1].append(request.user.Slot.baraban_2[i])
                        slot[2].append(request.user.Slot.baraban_2[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i - 2])
                        slot[1].append(request.user.Slot.baraban_3[i - 1])
                        slot[2].append(request.user.Slot.baraban_3[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i - 1])
                        slot[1].append(request.user.Slot.baraban_4[i])
                        slot[2].append(request.user.Slot.baraban_4[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i])
                        slot[1].append(request.user.Slot.baraban_5[i + 1])
                        slot[2].append(request.user.Slot.baraban_5[i + 2])
                        break

            elif bal_destr_elements[c] == "^":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i - 2])
                        slot[1].append(request.user.Slot.baraban_1[i - 1])
                        slot[2].append(request.user.Slot.baraban_1[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i - 1])
                        slot[1].append(request.user.Slot.baraban_2[i])
                        slot[2].append(request.user.Slot.baraban_2[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i])
                        slot[1].append(request.user.Slot.baraban_3[i + 1])
                        slot[2].append(request.user.Slot.baraban_3[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i - 1])
                        slot[1].append(request.user.Slot.baraban_4[i])
                        slot[2].append(request.user.Slot.baraban_4[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i - 2])
                        slot[1].append(request.user.Slot.baraban_5[i - 1])
                        slot[2].append(request.user.Slot.baraban_5[i])
                        break

            elif bal_destr_elements[c] == "Molnia":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i])
                        slot[1].append(request.user.Slot.baraban_1[i + 1])
                        slot[2].append(request.user.Slot.baraban_1[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i])
                        slot[1].append(request.user.Slot.baraban_2[i + 1])
                        slot[2].append(request.user.Slot.baraban_2[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i - 1])
                        slot[1].append(request.user.Slot.baraban_3[i])
                        slot[2].append(request.user.Slot.baraban_3[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i - 2])
                        slot[1].append(request.user.Slot.baraban_4[i - 1])
                        slot[2].append(request.user.Slot.baraban_4[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i - 2])
                        slot[1].append(request.user.Slot.baraban_5[i - 1])
                        slot[2].append(request.user.Slot.baraban_5[i])
                        break

            elif bal_destr_elements[c] == "ainloM":
                e = random.randint(0, 5)

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_1[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_1[i - 2])
                        slot[1].append(request.user.Slot.baraban_1[i - 1])
                        slot[2].append(request.user.Slot.baraban_1[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_2[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_2[i - 2])
                        slot[1].append(request.user.Slot.baraban_2[i - 1])
                        slot[2].append(request.user.Slot.baraban_2[i])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_3[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_3[i - 1])
                        slot[1].append(request.user.Slot.baraban_3[i])
                        slot[2].append(request.user.Slot.baraban_3[i + 1])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_4[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_4[i])
                        slot[1].append(request.user.Slot.baraban_4[i + 1])
                        slot[2].append(request.user.Slot.baraban_4[i + 2])
                        break

                trip_to_destroy = 0
                steps_to_destroy = random.randint(0, 50)
                for i in range(1000):
                    if request.user.Slot.baraban_5[i] == elements[e]:
                        trip_to_destroy += 1
                    if trip_to_destroy == steps_to_destroy:
                        slot[0].append(request.user.Slot.baraban_5[i])
                        slot[1].append(request.user.Slot.baraban_5[i + 1])
                        slot[2].append(request.user.Slot.baraban_5[i + 2])
                        break

            for i in range(3):
                print(slot[i])

            if slot[0][0] == slot[0][1] and slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3] and slot[0][3] == \
                    slot[0][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3]) or (
                    slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[0][2]) or (
                    slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3]) or (
                    slot[0][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка первой линии

            if slot[1][0] == slot[1][1] and slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3] and slot[1][3] == \
                    slot[1][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[1][0] == slot[1][1] and slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3]) or (
                    slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3] and slot[1][3] == slot[1][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[1][0] == slot[1][1] and slot[1][1] == slot[1][2]) or (
                    slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3]) or (
                    slot[1][2] == slot[1][3] and slot[1][3] == slot[1][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка второй линии

            if slot[2][0] == slot[2][1] and slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3] and slot[2][3] == \
                    slot[2][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3]) or (
                    slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[2][2]) or (
                    slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3]) or (
                    slot[2][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка третьей линии

            if slot[0][0] == slot[1][1] and slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3] and slot[1][3] == \
                    slot[0][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[1][1] and slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3]) or (
                    slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3] and slot[1][3] == slot[0][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[1][1] and slot[1][1] == slot[2][2]) or (
                    slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3]) or (
                    slot[2][2] == slot[1][3] and slot[1][3] == slot[0][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "V"

            if slot[2][0] == slot[1][1] and slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3] and slot[1][3] == \
                    slot[2][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[1][1] and slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3]) or (
                    slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3] and slot[1][3] == slot[2][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[1][1] and slot[1][1] == slot[0][2]) or (
                    slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3]) or (
                    slot[0][2] == slot[1][3] and slot[1][3] == slot[2][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "^"

            if slot[0][0] == slot[0][1] and slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3] and slot[2][3] == \
                    slot[2][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3]) or (
                    slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[1][2]) or (
                    slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3]) or (
                    slot[1][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "молния"

            if slot[2][0] == slot[2][1] and slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3] and slot[0][3] == \
                    slot[0][4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3]) or (
                    slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[1][2]) or (
                    slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3]) or (
                    slot[1][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "молния"(отзеркаленная)

            request.user.Slot.new_slot = slot
            for i in range(3):
                for j in range(5):
                    if slot[i][j] == "KC":
                        elements_image = Slots.objects.get(name="KC")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "ES":
                        elements_image = Slots.objects.get(name="ES")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "ZW":
                        elements_image = Slots.objects.get(name="ZW")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "SP":
                        elements_image = Slots.objects.get(name="SP")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "GE":
                        elements_image = Slots.objects.get(name="GE")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "KQ":
                        elements_image = Slots.objects.get(name="KQ")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "The Hand":
                        elements_image = Slots.objects.get(name="The Hand")
                        request.user.Slot.new_slot[i][j] = elements_image

            slot = request.user.Slot.new_slot

            if win_coef == 0:
                print("YOU LOST(( PROIZOSHLO RAZRUSHEINE BALANSA")
                msg = "YOU LOST(("
            else:
                print("YOU WON", stavka * win_coef, "PROIZOSHLO RAZRUSHEINE BALANSA")
                msg = "YOU WON"

            user = request.user
            user.initial_balance = user.initial_balance + stavka * win_coef
            user.save()

            print("TOTAL BALANCE:", request.user.initial_balance)

            request.user.Slot.count = random.randint(5, 10)
            request.user.Slot.balance_destroyer = 0

            return render(request, 'Menu/Slots.html', {'SLOT': slot, 'MSG': msg})

        elif request.user.Slot.balance_destroyer != request.user.Slot.count:

            win_coef = 0

            slot = [[], [], []]

            c = random.randint(1, 998)
            slot[0].append(request.user.Slot.baraban_1[c - 1])
            slot[1].append(request.user.Slot.baraban_1[c])
            slot[2].append(request.user.Slot.baraban_1[c + 1])

            c = random.randint(1, 998)
            slot[0].append(request.user.Slot.baraban_2[c - 1])
            slot[1].append(request.user.Slot.baraban_2[c])
            slot[2].append(request.user.Slot.baraban_2[c + 1])

            c = random.randint(1, 998)
            slot[0].append(request.user.Slot.baraban_3[c - 1])
            slot[1].append(request.user.Slot.baraban_3[c])
            slot[2].append(request.user.Slot.baraban_3[c + 1])

            c = random.randint(1, 998)
            slot[0].append(request.user.Slot.baraban_4[c - 1])
            slot[1].append(request.user.Slot.baraban_4[c])
            slot[2].append(request.user.Slot.baraban_4[c + 1])

            c = random.randint(1, 998)
            slot[0].append(request.user.Slot.baraban_5[c - 1])
            slot[1].append(request.user.Slot.baraban_5[c])
            slot[2].append(request.user.Slot.baraban_5[c + 1])

            for i in range(3):
                print(slot[i])

            if slot[0][0] == slot[0][1] and slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3] and slot[0][3] == \
                    slot[0][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3]) or (
                    slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[0][2]) or (
                    slot[0][1] == slot[0][2] and slot[0][2] == slot[0][3]) or (
                    slot[0][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка первой линии

            if slot[1][0] == slot[1][1] and slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3] and slot[1][3] == \
                    slot[1][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[1][0] == slot[1][1] and slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3]) or (
                    slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3] and slot[1][3] == slot[1][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[1][0] == slot[1][1] and slot[1][1] == slot[1][2]) or (
                    slot[1][1] == slot[1][2] and slot[1][2] == slot[1][3]) or (
                    slot[1][2] == slot[1][3] and slot[1][3] == slot[1][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка второй линии

            if slot[2][0] == slot[2][1] and slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3] and slot[2][3] == \
                    slot[2][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3]) or (
                    slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[2][2]) or (
                    slot[2][1] == slot[2][2] and slot[2][2] == slot[2][3]) or (
                    slot[2][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка третьей линии

            if slot[0][0] == slot[1][1] and slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3] and slot[1][3] == \
                    slot[0][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[1][1] and slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3]) or (
                    slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3] and slot[1][3] == slot[0][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[1][1] and slot[1][1] == slot[2][2]) or (
                    slot[1][1] == slot[2][2] and slot[2][2] == slot[1][3]) or (
                    slot[2][2] == slot[1][3] and slot[1][3] == slot[0][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "V"

            if slot[2][0] == slot[1][1] and slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3] and slot[1][3] == \
                    slot[2][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[1][1] and slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3]) or (
                    slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3] and slot[1][3] == slot[2][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[1][1] and slot[1][1] == slot[0][2]) or (
                    slot[1][1] == slot[0][2] and slot[0][2] == slot[1][3]) or (
                    slot[0][2] == slot[1][3] and slot[1][3] == slot[2][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "^"

            if slot[0][0] == slot[0][1] and slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3] and slot[2][3] == \
                    slot[2][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3]) or (
                    slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[0][0] == slot[0][1] and slot[0][1] == slot[1][2]) or (
                    slot[0][1] == slot[1][2] and slot[1][2] == slot[2][3]) or (
                    slot[1][2] == slot[2][3] and slot[2][3] == slot[2][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "молния"

            if slot[2][0] == slot[2][1] and slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3] and slot[0][3] == \
                    slot[0][
                        4]:
                win_coef += 10
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3]) or (
                    slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 5
                request.user.Slot.balance_destroyer += 1
            elif (slot[2][0] == slot[2][1] and slot[2][1] == slot[1][2]) or (
                    slot[2][1] == slot[1][2] and slot[1][2] == slot[0][3]) or (
                    slot[1][2] == slot[0][3] and slot[0][3] == slot[0][4]):
                win_coef += 2
                request.user.Slot.balance_destroyer += 1
            # Проверка комбинации "молния"(отзеркаленная)

            request.user.Slot.new_slot = slot
            for i in range(3):
                for j in range(5):
                    if slot[i][j] == "KC":
                        elements_image = Slots.objects.get(name="KC")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "ES":
                        elements_image = Slots.objects.get(name="ES")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "ZW":
                        elements_image = Slots.objects.get(name="ZW")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "SP":
                        elements_image = Slots.objects.get(name="SP")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "GE":
                        elements_image = Slots.objects.get(name="GE")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "KQ":
                        elements_image = Slots.objects.get(name="KQ")
                        request.user.Slot.new_slot[i][j] = elements_image
                    elif slot[i][j] == "The Hand":
                        elements_image = Slots.objects.get(name="The Hand")
                        request.user.Slot.new_slot[i][j] = elements_image

            slot = request.user.Slot.new_slot

            if win_coef == 0:
                print("YOU LOST((")
                msg = "YOU LOST(("
            else:
                print("YOU WON", stavka * win_coef)
                msg = "YOU WON " + str(stavka * win_coef) + " points."

            user = request.user
            user.initial_balance = user.initial_balance + stavka * win_coef
            user.save()
            print("TOTAL BALANCE:", request.user.initial_balance, request.user.Slot.balance_destroyer, request.user.Slot.count)

            return render(request, 'Menu/Slots.html', {'SLOT': slot, 'MSG': msg})



    return render(request, 'Menu/Slots.html')

def Slot_Machine_END(request):
    return render(request, 'Menu/SlotsEND.html')