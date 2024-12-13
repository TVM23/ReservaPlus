from django.db.models import Avg, Count, Q
from HotelApp.models import Servicios, Habitacion, DetalleHabitacion
from Reservas.models import Reseña, HabitacionesReservas


def get_relevant_items(user_input):
    # Categorías para servicios
    categories = {
        'relajación': ['cansado', 'dolores', 'relajar', 'estrés', 'descansar', 'spa', 'masaje', 'aguas termales'],
        'diversión': ['divertirse', 'fiesta', 'entretenimiento', 'juego', 'baile', 'música'],
        'comida': ['hambre', 'comer', 'restaurante', 'bar', 'cafetería'],
        'deporte': ['ejercicio', 'gimnasio', 'nadar', 'tenis', 'golf'],
    }

    # Categorías para habitaciones
    room_categories = {
        'lujo': ['suite', 'deluxe', 'lujosa', 'premium'],
        'familiar': ['familia', 'niños', 'amplia', 'grande'],
        'económica': ['barata', 'económica', 'presupuesto'],
        'vista': ['vista', 'panorámica', 'balcón'],
        'comodidades': ['jacuzzi', 'aire acondicionado', 'ventanas']
    }

    query = Q()
    room_query = Q()

    # Buscar palabras clave para servicios
    for category, keywords in categories.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            query |= Q(nombre__icontains=category) | Q(descripcion__icontains=category)
            for keyword in keywords:
                query |= Q(nombre__icontains=keyword) | Q(descripcion__icontains=keyword)

    # Buscar palabras clave para habitaciones
    for category, keywords in room_categories.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            room_query |= Q(nombre__icontains=category) | Q(detallehabitacion__ubicacion__icontains=category)
            for keyword in keywords:
                room_query |= Q(nombre__icontains=keyword) | Q(detallehabitacion__ubicacion__icontains=keyword)

    # Buscar por número de personas
    for number in range(1, 11):  # Asumimos un máximo de 10 personas
        if str(number) in user_input:
            room_query |= Q(cupo__gte=number)

    services = Servicios.objects.filter(query) if query else Servicios.objects.all()

    # Get rooms with their average review score
    rooms = Habitacion.objects.filter(room_query).annotate(
        avg_review=Avg('habitacionesreservas__reseña__reseña'),
        review_count=Count('habitacionesreservas__reseña')
    ).order_by('-avg_review', '-review_count').distinct()

    return services, rooms


def format_items_for_ai(services, rooms):
    services_info = ", ".join([f"{service.nombre}: {service.descripcion}" for service in services])

    rooms_info = []
    for room in rooms:
        avg_review = room.avg_review
        if avg_review is not None:
            avg_review_str = f"{avg_review:.1f}"
        else:
            avg_review_str = "N/A"

        room_info = (
            f"{room.nombre} (Capacidad: {room.cupo}, Precio: {room.precio}, "
            f"Calificación promedio: {avg_review_str}/5 basada en {room.review_count} reseñas): "
            f"{room.detallehabitacion_set.first().ubicacion if room.detallehabitacion_set.first() else 'Sin detalles'}"
        )
        rooms_info.append(room_info)

    rooms_info_str = ", ".join(rooms_info)
    return f"Servicios: {services_info}. Habitaciones: {rooms_info_str}"