from pydantic import BaseModel , Field
from datetime import date
class OrdersSchema(BaseModel):
    order_id : int 
    order_date : date
    customer_id :int
    order_status : str
    amount :int = Field(gt=0)

order_input={"order_id":1 ,"order_date":"2026-12-12", "customer_id":11, "order_status":"Delivered", "amount" : 100}

output_validated = OrdersSchema(**order_input)
if output_validated:
    print("Ek No..")
else:
    print("Check again .")