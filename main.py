
import uuid
import datetime
from datetime import time
import calendar
import cv2
import qrcode
import pymysql.cursors
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics.texture import Texture 

class Mysql():
    def conn():
        # Connect to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='qrcode_attendance',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection

class ViewUserInfoPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view_userinfo_msg = self.ids.view_userinfo_msg
        self.fname = self.ids.fname
        self.lname = self.ids.lname
        self.address = self.ids.address
        self.email = self.ids.email
        self.qrcode = self.ids.qrcode

    def get_user_info(self):
        conn = Mysql.conn()
        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM `users` WHERE `email`=%s"
                cursor.execute(sql, (self.put_user_email.text))
                result = cursor.fetchone()
                if result:
                    self.fname.text = result["fname"]
                    self.lname.text = result["lname"]
                    self.address.text = result["address"]
                    self.email.text = result["email"]
                    self.qrcode.source = f'qrcodes/{result["qrcode"]}'
                else:
                    self.view_userinfo_msg.text = "No user with this email"


class SetSchedPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_time_sched_msg = self.ids.set_time_sched_msg

    def set_time_sched(self):
        if self.time_in_start.text == "" or self.time_in_end.text == "" or self.time_out_start.text == "" or self.time_out_end.text == "":
            self.set_time_sched_msg.color = "red"
            self.set_time_sched_msg.text = "All fields are required"
            return

        in_start    = self.time_in_start.text.split(":")
        in_end      = self.time_in_end.text.split(":")
        out_start   = self.time_out_start.text.split(":")
        out_end     = self.time_out_end.text.split(":")

        if len(in_start) != 2 or len(in_end) != 2 or len(out_start) != 2 or len(out_end) != 2:
            self.set_time_sched_msg.color = "red"
            self.set_time_sched_msg.text = "Something is wrong with the inputs"
            return

        try:
            h1, m1 = map(int, in_start)
            res1 = time(hour=h1, minute=m1)
            h2, m2 = map(int, in_end)
            res2 = time(hour=h2, minute=m2)
            h3, m3 = map(int, out_start)
            res3 = time(hour=h3, minute=m3)
            h4, m4 = map(int, out_end)
            res4 = time(hour=h4, minute=m4)

            conn = Mysql.conn()
            with conn:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO `attendance_sched`(`sched_id`, `time_in_start`, `time_in_end`, `time_out_start`, `time_out_end`, `date`) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, ( uuid.uuid4(), res1, res2, res3, res4, datetime.datetime.now().strftime("%Y-%m-%d") ))
                    conn.commit()
                    self.set_time_sched_msg.color = "green"
                    self.set_time_sched_msg.text = "Attendace today was ready"
        except ValueError:
            self.set_time_sched_msg.color = "red"
            self.set_time_sched_msg.text = "Something is wrong with the inputs"
        
class MainLayout(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img1 = self.ids.img_renderer
        self.date_today = self.ids.date_today
        self.current_time = self.ids.current_time
        self.full_name = self.ids.full_name
        self.time_in = self.ids.time_in
        self.time_out = self.ids.time_out
        self.form_msg = self.ids.form_msg
        self.scan_status_msg = self.ids.scan_status_msg
        self.scan_status_msg.text = "Scanner is Ready"
        
        #opencv2 stuffs
        self.capture = cv2.VideoCapture(0)
        self.qr_detect = cv2.QRCodeDetector()

        # Check the attendance schedule for today
        attendace_info = self.check_attendance_sched()
        if attendace_info:
            self.ids.time_in_start_end.text = f'{attendace_info["time_in_start"]} - {attendace_info["time_in_end"]}'
            self.ids.time_out_start_end.text = f'{attendace_info["time_out_start"]} - {attendace_info["time_out_end"]}'
            self.ids.set_timesched_btn.disabled = True

        # Schedule the clock
        self.clock = Clock.schedule_interval(self.update_frame, 1.0/25.0)
        Clock.schedule_interval(self.update_time, 1)

    def open_timesched_popup(self):
        sp = SetSchedPopup()
        sp.open()
    
    def open_userview_popup(self):
        v = ViewUserInfoPopup()
        v.open()

    def check_attendance_sched(self):
        # Check if schedule for today was already exist 
        conn = Mysql.conn()
        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM `attendance_sched` WHERE `date`=%s"
                cursor.execute(sql, (datetime.datetime.now().strftime("%Y-%m-%d")))
                result = cursor.fetchone()
                return result

    def update_time(self, dt):
        date = datetime.datetime.now()
        self.date_today.text = date.strftime("%A, %d %B %Y")
        self.time = date.strftime("%I:%M:%S %p")
        self.current_time.text =  self.time

    def get_lastday_in_month(self):
        date = datetime.date.today()
        year = int(date.strftime("%Y"))
        month = int(date.strftime("%m"))
        last_day = calendar.monthrange(year, month)[1]
        return last_day

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        cv2.rectangle(frame, (150, 75), (500, 400), (255, 195, 0), 1)
        # Decoding the qr code
        decoded_data, pts, st_code = self.qr_detect.detectAndDecode(frame)

        # If data is being read then do somthing 
        if(decoded_data):
            cv2.putText(frame, "Detected", (250, 70), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 195, 0), 1, cv2.LINE_AA)
            # Stop the render of the frame
            Clock.unschedule(self.clock)

            # Process the attendance
            self.process_attendance(decoded_data)

            # Restart the process
            Clock.schedule_once(self.restart, 3)
        
        # convert it to texture
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(
            size=(frame.shape[1],
            frame.shape[0]),
            colorfmt='bgr'
        ) 
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture

    def process_attendance(self, user_id):
        # Check if data is valid
        # Check the attendance sched for today
        sched = self.check_attendance_sched()
        if sched:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            cur_time = current_time.split(":")
            # cur_time = "20:50:00".split(":")

            time_in_start = sched["time_in_start"].split(":")
            time_in_end = sched["time_in_end"].split(":")
            time_out_start = sched["time_out_start"].split(":")
            time_out_end = sched["time_out_end"].split(":")
            conn = Mysql.conn()

            with conn:
                with conn.cursor() as cursor:
                    # Get the user's info
                    sql1 = "SELECT * FROM `users` WHERE `user_id`=%s"
                    cursor.execute(sql1, (user_id))
                    user_info = cursor.fetchone() 
                    if not user_info:
                        self.scan_status_msg.color = "red"
                        self.scan_status_msg.text = "User is not recognized"
                        return

                    if(int(cur_time[0]) < int(time_in_end[0]) or (int(cur_time[0]) == int(time_in_end[0]) and int(cur_time[1]) < int(time_in_end[1]))):
                        # Check if user has been timein already
                        sql1 = "SELECT * FROM `records` WHERE `user_id`=%s"
                        cursor.execute(sql1, (user_id))
                        result = cursor.fetchone()
                        if result:
                            self.scan_status_msg.color = "yellow"
                            self.scan_status_msg.text = "You have been time in already"
                        else:
                            if int(cur_time[0]) < int(time_in_start[0]) or (int(cur_time[0]) == int(time_in_start[0]) and int(cur_time[1]) < int(time_in_start[1])):
                                self.scan_status_msg.color = "red"
                                self.scan_status_msg.text = "Time in not yet started"
                            else:
                                # Processing time in
                                sql = "INSERT INTO `records` (`record_id`, `sched_id`, `user_id`, `time_in`) VALUES(%s, %s, %s, %s)"
                                cursor.execute(sql, (uuid.uuid4(), sched["sched_id"], user_id, current_time))
                                conn.commit()
                                self.full_name.text = f'{user_info["fname"]} {user_info["lname"]}'
                                self.time_in.text = current_time
                                self.scan_status_msg.color = "lightgreen"
                                self.scan_status_msg.text = "Time in successful"
                    else:
                        if int(cur_time[0]) < int(time_out_start[0]) or (int(cur_time[0]) == int(time_out_start[0]) and int(cur_time[1]) < int(time_out_start[1])):
                            self.scan_status_msg.color = "red"
                            self.scan_status_msg.text = "Time out not yet started"
                        elif int(cur_time[0]) > int(time_out_end[0]) or (int(cur_time[0]) == int(time_out_end[0]) and int(cur_time[1]) > int(time_out_end[1])):
                            print(cur_time)
                            self.scan_status_msg.color = "red"
                            self.scan_status_msg.text = "Time out is over"
                        else:
                            # Check if user have a time in record 
                            sql2 = "SELECT * FROM `records` WHERE `sched_id`=%s and `user_id`=%s"
                            cursor.execute(sql2, (sched["sched_id"], user_id))
                            result = cursor.fetchone()
                            if result:
                                # Check if user have been timeout already
                                if(result["time_out"]):
                                    self.scan_status_msg.color = "yellow"
                                    self.scan_status_msg.text = "You have been timeout already"
                                else:
                                    sql3 = "UPDATE `records` SET `time_out`=%s WHERE `record_id`=%s"
                                    cursor.execute(sql3, (current_time, result["record_id"]))
                                    conn.commit()
                                    self.scan_status_msg.color = "lightgreen"
                                    self.scan_status_msg.text = "Time out successful"
                                    self.full_name.text = f'{user_info["fname"]} {user_info["lname"]}'
                                    self.time_out.text = current_time
                            else:
                                self.scan_status_msg.color = "red"
                                self.scan_status_msg.text = "Can't time out, you have no time in record"
        else:
            self.scan_status_msg.color = "red"
            self.scan_status_msg.text = "No time schedule for today"

    def add_user(self):
        # Check text input if it is empty then return the process
        if  self.fname.text == "" or self.lname.text == "" or self.address.text == "" or self.email.text == "":
            self.form_msg.color = "red"
            self.form_msg.text = "All fields are required"
            return

        # Get automatically the value of a input text
        user_id = uuid.uuid4()

        user_data =  (user_id,
            self.fname.text,
            self.lname.text,
            f'{user_id}.png',
            self.address.text,
            self.email.text)
        
        conn = Mysql.conn()
        with conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO `users`(`user_id`, `fname`, `lname`, `qrcode`, `address`, `email`) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, user_data)
                conn.commit()

                # Generate qrcode and pass the person uuid as data of the qrcode
                qr = qrcode.QRCode(version=1, box_size = 15, border = 5)
                qr.add_data(user_id)
                qr.make(fit=True)
                img = qr.make_image(fill='green', back_color='lightblue')
                img.save(f'qrcodes/{user_id}.png')
                        
                # Show success message
                self.form_msg.color = "green"
                self.form_msg.text = "Person added successfully"

                # Clear the text feild
                self.fname.text = ""
                self.lname.text = ""
                self.address.text = ""
                self.email.text = ""

    def restart(self, dt):
        self.full_name.text = "Waiting"
        self.time_in.text = "Waiting"
        self.time_out.text = "Waiting"
        self.scan_status_msg.color = "white"
        self.scan_status_msg.text = "Scanner is Ready"
        self.clock = Clock.schedule_interval(self.update_frame, 1.0/25.0)

class QrCodeAttendanceApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    QrCodeAttendanceApp().run()
