from django.shortcuts import render


def agregar_habitacion(request):
    return render(request, 'agregar_habitacion.html')
