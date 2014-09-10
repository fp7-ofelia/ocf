from django.dispatch import Signal

def post_object_ready(instance):
    # Send signal "post_object_ready" when generic object is ready
    post_object_ready = Signal()
    post_object_ready.send_robust(sender=type(instance).__name__)
