from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

@app.api_route("/", methods=["GET", "POST"])
async def handle_request(request: Request):
    if request.method == "GET":
        return JSONResponse(content={"message": "Webhook endpoint is alive. Use POST for requests."})

    # POST handling
    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        'order.add - context:ongoing-order': add_to_order,
        'order.remove - context:ongoing-order': remove_from_order,
        'order.complete - context:ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters, session_id)
    else:
        return JSONResponse(content={
            'fulfillmentText': f"No handler found for intent: {intent}"
        })


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = 'I am having trouble finding your order. Sorry, can you place the order again?'
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry! I couldn't process your order due to backend error. Please place a new order again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = (
                f'Awesome! We have placed your order.\n'
                f'Your order id is #{order_id}.\n'
                f'Your order total is {order_total}, which you can pay at the time of delivery.'
            )
        del inprogress_orders[session_id]

    return JSONResponse(content={'fulfillmentText': fulfillment_text})


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1
    db_helper.insert_order_tracking(next_order_id, 'in progress')
    return next_order_id


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters.get('food-item', [])
    quantities = parameters.get('number', [])

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Please specify food items and quantities clearly."
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        print(inprogress_orders)
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={'fulfillmentText': fulfillment_text})


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            'fulfillmentText': 'I am having trouble finding your order. Sorry! Can you place it again?'
        })

    current_order = inprogress_orders[session_id]
    food_items = parameters.get('food-item', [])
    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    fulfillment_text_parts = []
    if removed_items:
        fulfillment_text_parts.append(f"Removed {', '.join(removed_items)} from your order.")
    if no_such_items:
        fulfillment_text_parts.append(f"Your current order does not have {', '.join(no_such_items)}.")
    if not current_order:
        fulfillment_text_parts.append("Your order is empty!")
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text_parts.append(f"Here is what is left of your order: {order_str}")

    return JSONResponse(content={'fulfillmentText': " ".join(fulfillment_text_parts)})


def track_order(parameters: dict, session_id: str):
    order_id = parameters.get('order_id')
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={'fulfillmentText': fulfillment_text})