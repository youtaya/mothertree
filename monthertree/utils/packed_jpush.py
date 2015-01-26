import jpush as jpush
from monthertree.conf import app_key, master_secret

def jpush_send_message(push_src, push_target, id):
	_jpush = jpush.JPush(app_key, master_secret)
	push = _jpush.create_push()
	push.audience = jpush.audience(
		# push_target may user account or phone number
		jpush.tag(push_target)
	)
	push.message = jpush.message(msg_content=id, extras=str(push_src))
	push.platform = jpush.all_
	push.send()
