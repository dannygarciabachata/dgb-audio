"""
DGB AUDIO - Stripe Payment Service
===================================
Handle subscriptions, checkout, and webhooks with Stripe.
"""

import os
import stripe
from datetime import datetime
from typing import Optional
from pathlib import Path
import json

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Initialize Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Price IDs (replace with your actual Stripe Price IDs)
PRICE_IDS = {
    "starter": None,  # Free plan, no Stripe price
    "creator": os.getenv("STRIPE_PRICE_CREATOR", "price_creator_monthly"),
    "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_monthly"),
    "studio": os.getenv("STRIPE_PRICE_STUDIO", "price_studio_monthly")
}

# Plan details for display
PLAN_DETAILS = {
    "starter": {
        "name": "Starter",
        "price_monthly": 0,
        "storage_gb": 1,
        "recording_seconds": 30,
        "max_projects": 2,
        "features": ["1GB storage", "2 proyectos", "Grabación 30s", "Chat soporte"]
    },
    "creator": {
        "name": "Creator",
        "price_monthly": 19,
        "storage_gb": 10,
        "recording_seconds": 60,
        "max_projects": 20,
        "features": ["10GB storage", "20 proyectos", "Grabación 60s", "Prioridad media"]
    },
    "pro": {
        "name": "Pro",
        "price_monthly": 49,
        "storage_gb": 50,
        "recording_seconds": -1,
        "max_projects": -1,
        "features": ["50GB storage", "∞ proyectos", "Grabación ilimitada", "Soporte prioritario"]
    },
    "studio": {
        "name": "Studio",
        "price_monthly": 149,
        "storage_gb": 200,
        "recording_seconds": -1,
        "max_projects": -1,
        "features": ["200GB storage", "∞ proyectos", "API access", "Soporte VIP 24/7"]
    }
}


def get_plans() -> list:
    """Get all available plans"""
    return [
        {
            "id": plan_id,
            **details,
            "stripe_price_id": PRICE_IDS.get(plan_id)
        }
        for plan_id, details in PLAN_DETAILS.items()
    ]


async def create_checkout_session(
    user_email: str,
    user_id: str,
    plan: str
) -> dict:
    """
    Create a Stripe checkout session for subscription.
    """
    if not STRIPE_SECRET_KEY:
        return {"error": "Stripe not configured", "demo_mode": True}
    
    if plan == "starter":
        return {"error": "Starter plan is free, no payment needed"}
    
    price_id = PRICE_IDS.get(plan)
    if not price_id:
        return {"error": f"Invalid plan: {plan}"}
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{FRONTEND_URL}/dashboard?payment=success&plan={plan}",
            cancel_url=f"{FRONTEND_URL}/pricing?payment=cancelled",
            customer_email=user_email,
            metadata={
                "user_id": user_id,
                "plan": plan
            },
            subscription_data={
                "metadata": {
                    "user_id": user_id,
                    "plan": plan
                }
            }
        )
        
        return {
            "success": True,
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except stripe.error.StripeError as e:
        return {"error": str(e)}


async def create_billing_portal_session(customer_id: str) -> dict:
    """
    Create a Stripe billing portal session for managing subscription.
    """
    if not STRIPE_SECRET_KEY:
        return {"error": "Stripe not configured"}
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{FRONTEND_URL}/dashboard"
        )
        
        return {
            "success": True,
            "portal_url": session.url
        }
        
    except stripe.error.StripeError as e:
        return {"error": str(e)}


async def handle_webhook(payload: bytes, signature: str) -> dict:
    """
    Handle Stripe webhook events.
    """
    if not STRIPE_WEBHOOK_SECRET:
        return {"error": "Webhook secret not configured"}
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return {"error": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}
    
    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]
    
    if event_type == "checkout.session.completed":
        # Payment successful, activate subscription
        user_id = data.get("metadata", {}).get("user_id")
        plan = data.get("metadata", {}).get("plan")
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        
        if user_id and plan:
            # Update user's plan in database
            from services.auth_service import _load_users, _save_users
            users = _load_users()
            
            for email, user in users.items():
                if user.get("id") == user_id:
                    users[email]["plan"] = plan
                    users[email]["stripe_customer_id"] = customer_id
                    users[email]["stripe_subscription_id"] = subscription_id
                    users[email]["subscription_status"] = "active"
                    users[email]["updated_at"] = datetime.now().isoformat()
                    
                    # Update limits based on plan
                    plan_limits = {
                        "starter": {"storage_gb": 1, "recording_seconds": 30, "max_projects": 2},
                        "creator": {"storage_gb": 10, "recording_seconds": 60, "max_projects": 20},
                        "pro": {"storage_gb": 50, "recording_seconds": -1, "max_projects": -1},
                        "studio": {"storage_gb": 200, "recording_seconds": -1, "max_projects": -1}
                    }
                    users[email]["limits"] = plan_limits.get(plan, plan_limits["starter"])
                    break
            
            _save_users(users)
            return {"success": True, "action": "subscription_activated", "plan": plan}
    
    elif event_type == "customer.subscription.updated":
        # Subscription updated (plan change, renewal, etc.)
        subscription_id = data.get("id")
        status = data.get("status")
        
        from services.auth_service import _load_users, _save_users
        users = _load_users()
        
        for email, user in users.items():
            if user.get("stripe_subscription_id") == subscription_id:
                users[email]["subscription_status"] = status
                users[email]["updated_at"] = datetime.now().isoformat()
                break
        
        _save_users(users)
        return {"success": True, "action": "subscription_updated", "status": status}
    
    elif event_type == "customer.subscription.deleted":
        # Subscription cancelled
        subscription_id = data.get("id")
        
        from services.auth_service import _load_users, _save_users
        users = _load_users()
        
        for email, user in users.items():
            if user.get("stripe_subscription_id") == subscription_id:
                users[email]["plan"] = "starter"
                users[email]["subscription_status"] = "cancelled"
                users[email]["limits"] = {"storage_gb": 1, "recording_seconds": 30, "max_projects": 2}
                users[email]["updated_at"] = datetime.now().isoformat()
                break
        
        _save_users(users)
        return {"success": True, "action": "subscription_cancelled"}
    
    elif event_type == "invoice.payment_failed":
        # Payment failed
        customer_id = data.get("customer")
        
        from services.auth_service import _load_users, _save_users
        users = _load_users()
        
        for email, user in users.items():
            if user.get("stripe_customer_id") == customer_id:
                users[email]["subscription_status"] = "past_due"
                users[email]["updated_at"] = datetime.now().isoformat()
                break
        
        _save_users(users)
        return {"success": True, "action": "payment_failed"}
    
    return {"success": True, "action": "ignored", "event_type": event_type}


def get_subscription_status(user_email: str) -> dict:
    """Get user's subscription status"""
    from services.auth_service import _load_users
    users = _load_users()
    
    if user_email not in users:
        return {"error": "User not found"}
    
    user = users[user_email]
    
    return {
        "plan": user.get("plan", "starter"),
        "subscription_status": user.get("subscription_status", "free"),
        "stripe_customer_id": user.get("stripe_customer_id"),
        "has_active_subscription": user.get("subscription_status") == "active"
    }
