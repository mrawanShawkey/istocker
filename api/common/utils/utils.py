from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.extentions.extentions import bcrypt

def get_user_id_with_uuid(uuid):
    uuid = convert_uuid_str_to_UUID(uuid)
    user = User.query.filter_by(uuid=uuid).first()
    if user:
        return user.user_id
    else:
        raise Errors.UserNotFound
    
def convert_uuid_str_to_UUID(uuid):
    return PyUUID(uuid) if isinstance(uuid, str) else uuid

def required_fields_exist(required_fields, payload):
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise Errors.InvalidInput
    else:
        return True

def verify_password(hash, password):
    if bcrypt.check_password_hash(hash, password):
        return True
    else:
        raise Errors.IncorrectCredentials
    
def verify_patch_keys(payload):
    if not payload:
        return None
    if 'modifications' not in payload:
        raise Errors.ValidationFailed
    modifications = payload['modifications']
    if isinstance(modifications, list) and len(modifications) == 0:
        return None
    else:
        return modifications
    
def apply_db_updates(record, ALLOWED_UPDATES, modifications):
        is_updated = False
        try:
            for mod in modifications:
                field = mod.get('field')
                new_value = mod.get('value')
                if field in ALLOWED_UPDATES:
                    db_column = ALLOWED_UPDATES[field]
                    setattr(record, db_column, new_value)
                    is_updated = True
            if is_updated:
                db.session.commit()
        except (AppErrors, Exception) as e:
            db.session.rollback()
            if isinstance(e, AppErrors):
                raise e
            else:
                raise Errors.DatabaseError
            
def get_reset_pass_html(reset_code):
    body = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 0; }}
            .container {{ max-width: 550px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
            .header {{ background-color: #0f172a; padding: 35px 20px; text-align: center; color: #ffffff; }}
            .header h2 {{ margin: 10px 0 0 0; font-size: 22px; font-weight: 500; letter-spacing: 0.5px; }}
            .shield-icon {{ font-size: 36px; line-height: 1; }}
            .content {{ padding: 40px 35px; line-height: 1.6; font-size: 15px; }}
            .greeting {{ font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 15px; }}
            .code-box {{ background-color: #f1f5f9; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 15px 20px; text-align: center; margin: 25px 0; font-family: 'Courier New', Courier, monospace; font-size: 14px; color: #334155; word-break: break-all; font-weight: bold; }}
            .button-container {{ text-align: center; margin: 30px 0 10px 0; }}
            .btn {{ background-color: #2563eb; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block; font-size: 15px; box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2); }}
            .warning {{ font-size: 13px; color: #64748b; margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 20px; }}
            .footer {{ background-color: #f8fafc; text-align: center; padding: 20px; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="shield-icon">🛡️</div>
                <h2>Account Security Services</h2>
            </div>
            <div class="content">
                <p class="greeting">Password Reset Request</p>
                <p>We received a request to reset the password for the iStocker account associated with this email address.</p>
                <p>To proceed with setting up a new password, please copy the secret authorization token below and paste it into the reset form window on our application workspace:</p>
                
                <div class="code-box">
                    {reset_code}
                </div>
                
                <div class="button-container">
                    <a href="https://istocker.vercel.app/reset-password" class="btn">Go to Reset Portal</a>
                </div>
                
                <p class="warning">
                    <strong>Didn't request this change?</strong><br>
                    If you did not make this request, you can safely ignore this email. Your current credentials remain fully secure and your account will not be modified.
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    return body
            
def get_market_update_html():
    body = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e1e4e8; }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: #ffffff; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
            .content {{ padding: 30px; line-height: 1.6; font-size: 16px; }}
            .button-container {{ text-align: center; margin: 25px 0; }}
            .btn {{ background-color: #2a5298; color: #ffffff !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }}
            .footer {{ background-color: #f8f9fa; text-align: center; padding: 15px; font-size: 12px; color: #6c757d; border-top: 1px solid #e1e4e8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>iStocker Financial Engineering Platform</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Today's trading session on the <strong>Egyptian Exchange (EGX30)</strong> has concluded. Our machine learning pipelines have processed the latest data and updated your personalized portfolio tracking analytics.</p>
                <p>New optimized predictions and risk-adjusted recommendations are now available for your designated profile risk tier (Conservative, Moderate, or Aggressive).</p>
                
                <div class="button-container">
                    <a href="https://istocker.vercel.app" class="btn">View Dashboard Analytics</a>
                </div>
                
                <p>Best regards,<br><strong>The iStocker Quantum Team</strong></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return body