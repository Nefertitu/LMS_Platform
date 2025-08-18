import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Tuple, Union

import stripe
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from config.settings import STRIPE_API_KEY
from materials.models import Course, Lesson

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(obj: Union[Course, Lesson]) -> stripe.Product:
    """Создает новый продукт в Stripe (курс или урок)"""

    product_name = obj.course_title if hasattr(obj, "course_title") else obj.title
    product = stripe.Product.create(
        name=product_name,
    )
    return product


def create_stripe_price(product: stripe.Product, amount: Decimal) -> stripe.Price:
    """Создает цену для продукта в Stripe"""

    return stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),
        product=product.id,
    )


def create_stripe_session(price: stripe.Price) -> Tuple[str, str | None]:
    """Создает платежную сессию в Stripe"""

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/payment/",
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
    )

    return session.id, session.url


def create_retrieves_a_checkout_session(session_id: str) -> Dict[str, Any]:
    """Получает информацию о платежной сессии из Stripe"""

    session_result = stripe.checkout.Session.retrieve(session_id)
    # print(f"Результат платежа: {session_result}")

    customer_email = None
    if hasattr(session_result, "customer_details") and session_result.customer_details:
        customer_email = getattr(session_result.customer_details, "email", None)

    session_data = {
        "amount": session_result.amount_total,
        "status": session_result.payment_status,
        "currency": session_result.currency,
        "email": customer_email,
        "payment_intent_id": session_result.payment_intent,
    }
    # print(f"Статус: {session_data['status']}")

    return session_data
