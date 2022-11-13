import os
from bleach import clean
import uvicorn
from fastapi import FastAPI, Request, Form
from starlette.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pymongo import MongoClient
from typing import Optional
from models.models import UserRegForm, editForm
import random, string
import smtplib
from email.message import EmailMessage
from bson import ObjectId
from dotenv import load_dotenv

# init
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="client")

load_dotenv()

MONGODB_CONNECTION_URI = os.getenv("MONGODB_CONNECTION_URI")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# the db stuff
client = MongoClient(MONGODB_CONNECTION_URI)
db = client["parkIn"]
part_form = db["users"]
ticket = db["tickets"]

try:
    client.admin.command("ping")
    print("Successfully connected to the database!")
except:
    print("Database connection refused. Please check status of database!")

# part_form.insert_one({"username":"shourya.de12@gmail.com","fullname":"Shourya De","password":"hellohello","admin":True,"phone":"","yearvalid":2027})


@app.get("/", response_class=HTMLResponse, tags=["GET Register Page"])
async def register(request: Request):
    # render stuff
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse, tags=["POST Endpoint to Register Teams"])
async def login(
    request: Request,
    username: Optional[str] = Form(...),
    password: Optional[str] = Form(...),
    phone: Optional[int] = Form(...),
):

    if bool(
        part_form.find_one({"username": username, "password": password, "phone": phone})
    ):
        if bool(part_form.find_one({"username": username, "admin": True})):
            admindata = part_form.find_one({"username": username, "admin": True})
            return templates.TemplateResponse(
                "/admin/user.html",
                {
                    "request": request,
                    "username": username,
                    "viewticket": "viewticket",
                    "adduser": "adduser",
                    "edit": "edit",
                    "resolve": "resolve",
                    "fullname": admindata["fullname"],
                    "status": "Admin",
                    "yearvalid": admindata["yearvalid"],
                },
            )
        else:
            data = part_form.find_one({"username": username})
            return templates.TemplateResponse(
                "user.html",
                {
                    "request": request,
                    "verificationwall": "verificationwall",
                    "raise": "raise",
                    "pay": "pay",
                    "fullname": data["fullname"],
                    "vehicle": data["vehicle"],
                    "yearvalid": data["yearvalid"],
                    "status": data["status"],
                    "username": data["username"],
                },
            )
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "em": "Invalid Credentials or User doesn't exist. Please contact your admin.",
            },
        )


# user button stuff


@app.get("/pay", response_class=HTMLResponse, tags=["GET Register Page"])
async def pay(request: Request):
    return templates.TemplateResponse("pay.html", {"request": request})


@app.get("/raise", response_class=HTMLResponse, tags=["GET Register Page"])
async def raiser(request: Request):
    return templates.TemplateResponse("raise.html", {"request": request})


@app.get("/verificationwall", response_class=HTMLResponse, tags=["GET Register Page"])
async def raiser(request: Request):
    return templates.TemplateResponse("verificationwall.html", {"request": request})


@app.get("/viewtickets", response_class=HTMLResponse, tags=["GET Register Page"])
async def viewtickets(request: Request):
    return templates.TemplateResponse("viewtickets.html", {"request": request})


@app.post("/raise", response_class=HTMLResponse, tags=["GET Register Page"])
async def raiser(
    request: Request,
    username: Optional[str] = Form(...),
    phone: Optional[int] = Form(...),
    fullname: Optional[str] = Form(...),
    email: Optional[str] = Form(...),
    msg: Optional[str] = Form(...),
):

    try:
        message = EmailMessage()
        message.set_content(msg)
        message["Subject"] = "Support Request for {}, Phone Number {}".format(
            fullname, phone
        )
        message["To"] = email
        message["From"] = "parkin.messages2022@gmail.com"
        message["Cc"] = username
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("parkin.messages2022@gmail.com", SMTP_PASSWORD)
        server.send_message(message)
        server.quit()
        print("Email sent successfully!")

    except Exception as ex:
        print("Something went wrong....", ex)
        return templates.TemplateResponse("error.html", {"request": request, "em": ex})
    return templates.TemplateResponse(
        "success.html", {"request": request, "sm": "Request Raised Successfully!"}
    )


@app.post("/verificationwall", response_class=HTMLResponse, tags=["POST Register Page"])
async def verify(
    request: Request,
    username: Optional[str] = Form(...),
    password: Optional[str] = Form(...),
):
    if bool(part_form.find_one({"username": username, "password": password})):
        # ticket.insert_one({"username":"rochak@123","vehicle":"IAMLATE","resolved":False,"time":"17-05-2003 23:11"})
        # ticket.insert_one({"username":"rochak@123","vehicle":"IAMLATE","resolved":True,"time":"17-05-2003 23:12"})
        query1 = ticket.find({"username": username})
        query1 = list(query1)
        query2 = ticket.find({"username": username, "resolved": True})
        query2 = list(query2)
        return templates.TemplateResponse(
            "viewtickets.html",
            {
                "request": request,
                "len": len(query1),
                "ticketlist": query1,
                "username": username,
                "length": len(query2),
            },
        )
    else:
        return templates.TemplateResponse(
            "error.html", {"request": request, "em": "Wrong Credentials Provided!"}
        )


@app.get("/admin/adduser", response_class=HTMLResponse, tags=["GET Register Page"])
async def register(request: Request):
    return templates.TemplateResponse("/admin/adduser.html", {"request": request})


@app.get("/admin/viewticket", response_class=HTMLResponse, tags=["GET Register Page"])
async def viewticket(request: Request):
    query1 = ticket.find({"resolved": False})
    query1 = list(query1)
    return templates.TemplateResponse(
        "/admin/viewticket.html", {"request": request, "ticketlist": query1}
    )


@app.get("/admin/edit", response_class=HTMLResponse, tags=["GET Register Page"])
async def edit(request: Request):
    return templates.TemplateResponse("/admin/edit.html", {"request": request})


@app.get("/admin/resolve", response_class=HTMLResponse, tags=["GET Register Page"])
async def resolve(request: Request):
    return templates.TemplateResponse("/admin/resolve.html", {"request": request})


@app.post("/admin/adduser", response_class=HTMLResponse, tags=["POST Register Page"])
async def register(
    request: Request,
    username: Optional[str] = Form(...),
    phone: Optional[int] = Form(...),
    fullname: Optional[str] = Form(...),
    vehicle: Optional[str] = Form(...),
    status: Optional[str] = Form(...),
    yearvalid: Optional[int] = Form(...),
    password: Optional[str] = "".join(
        random.choices(string.ascii_letters + string.digits, k=6)
    ),
    admin: Optional[bool] = False,
):

    user = UserRegForm(
        username=clean(username),
        phone=phone,
        fullname=clean(fullname),
        vehicle=clean(vehicle),
        status=clean(status),
        yearvalid=yearvalid,
        password=password,
        admin=admin,
    )
    if bool((part_form.find_one({"username": username}))):
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "em": "Email ID already registered. Please register with new Email ID",
            },
        )
    else:
        part_form.insert_one(user.dict())
        return templates.TemplateResponse(
            "success.html", {"request": request, "sm": "Sucessful Registration!"}
        )


@app.post("/admin/edit", response_class=HTMLResponse, tags=["POST Register Page"])
async def register(
    request: Request,
    username: Optional[str] = Form(...),
    phone: Optional[int] = Form(...),
    fullname: Optional[str] = Form(...),
    vehicle: Optional[str] = Form(...),
    status: Optional[str] = Form(...),
    yearvalid: Optional[int] = Form(...),
    admin: Optional[bool] = False,
):
    user = editForm(
        username=clean(username),
        phone=phone,
        fullname=clean(fullname),
        vehicle=clean(vehicle),
        status=clean(status),
        yearvalid=yearvalid,
        admin=admin,
    )

    if bool((part_form.find_one({"username": username}))):
        query1 = part_form.find_one({"username": username})
        query = {"_id": ObjectId(query1["_id"])}
        part_form.replace_one(query, user.dict())
        return templates.TemplateResponse(
            "success.html",
            {
                "request": request,
                "sm": "User Details Modified",
            },
        )
    else:
        return templates.TemplateResponse(
            "error.html", {"request": request, "em": "No such user!"}
        )


@app.post("/admin/resolve", response_class=HTMLResponse, tags=["POST Register Page"])
async def register(
    request: Request,
    username: Optional[str] = Form(...),
    vehicle: Optional[str] = Form(...),
    fullname: Optional[str] = Form(...),
    time: Optional[str] = Form(...),
    password: Optional[str] = Form(...),
):
    if bool(
        ticket.find_one(
            {"username": username, "time": time, "vehicle": vehicle, "resolved": False}
        )
    ):
        if bool(
            part_form.find_one(
                {"fullname": fullname, "password": password, "admin": True}
            )
        ):
            query1 = ticket.find_one(
                {"username": username, "time": time, "vehicle": vehicle}
            )
            query = {"_id": ObjectId(query1["_id"])}
            ticket.replace_one(
                query,
                {
                    "username": username,
                    "time": time,
                    "vehicle": vehicle,
                    "resolved": True,
                },
            )
            return templates.TemplateResponse(
                "success.html",
                {
                    "request": request,
                    "sm": "Payment Resolved!",
                },
            )
        else:
            return templates.TemplateResponse(
                "error.html", {"request": request, "em": "Unauthorized Request!"}
            )
    else:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "em": "Record Doesn't Exist on the Database!"},
        )
