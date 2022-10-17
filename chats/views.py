from django.shortcuts import render

def room(request, order_id):
    return render(request,"chat_room.html",{"room_name_json": str(order_id)})

