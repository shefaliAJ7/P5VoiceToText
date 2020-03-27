from flask import request, flash, jsonify, Blueprint, render_template
from flask_cors import cross_origin
from P5VoiceToText.config import Config
from P5VoiceToText.files.voiceTextConversionUtils import VoiceText

import os
import time
from werkzeug.utils import secure_filename
from P5VoiceToText.files.voiceFilesUtils import AudioFile

files = Blueprint('files', __name__)

# Import all config related variables
upload_folder = Config.UPLOAD_FOLDER
cors_ip = Config.DEV_IP
cors_header = Config.CORS_HEADERS
allowed_extensions = Config.ALLOWED_EXTENSIONS
aws_allowed_extensions = Config.AWS_ALLOWED_EXTENSIONS

aws_access_key_id = Config.ACCESS_KEY_ID
aws_access_secret_key = Config.ACCESS_SECRET_KEY
aws_bucket_name = Config.BUCKET_NAME


@files.route("/files", methods=['GET'])
def get_all_files():
	try:
		audio_file = AudioFile()
		voice_files = audio_file.get_all_files_db()
		files = []
		for voice_file in voice_files:
			files.append(voice_file.filename)
		message = {
			"files": files
		}
		return jsonify(message), 200
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500


@cross_origin(origin=cors_ip,headers=cors_header)
@files.route("/files", methods=['POST'])
def add_new_file():
	try:
		# if the file is not present in the request, reject it
		if 'file' not in request.files:
			message = {
				"message": "file value not found in the request"
			}
			return jsonify(message), 400

		file = request.files['file']
		filename = file.filename
		filename_without_extension = os.path.splitext(filename)[0]
		extension = os.path.splitext(filename)[1]

		# Check if the file is of proper extension
		if len(extension) > 0 and extension[1:].lower() not in allowed_extensions:
			message = {
				"message": "Invalid file type",
				"allowed_formats": str(allowed_extensions)
			}
			return jsonify(message), 400

		audio_file = AudioFile()
		audio_file.filename = filename
		file_complete_path = ''

		# Save the file locally
		if file:
			if not os.path.isdir(upload_folder):
				os.mkdir(upload_folder)
			filename = secure_filename(file.filename)
			destination = "/".join([upload_folder, filename])
			file.save(destination)
			file_complete_path = destination

		if len(extension) > 0 and extension[1:].lower() not in aws_allowed_extensions:
			audio_file.filename = filename
			audio_file.change_media(file_complete_path)
			filename = audio_file.filename
			file_complete_path = upload_folder + filename

		filename_without_extension = os.path.splitext(audio_file.filename)[0]
		extension = os.path.splitext(audio_file.filename)[1]

		# If file exists in DB rename it
		if audio_file.check_filename_exists() :
			timestamp = time.strftime('%Y%m%d%H%M%S')
			filename = filename_without_extension + timestamp + extension
			rename_file_path = upload_folder + filename
			os.rename(file_complete_path, rename_file_path)
			file_complete_path = rename_file_path

		audio_file.filename = filename
		s3Link = audio_file.store_file_aws(file_complete_path)

		os.remove(file_complete_path)

		audio_file = AudioFile()
		audio_file.filename = filename
		audio_file.s3link = s3Link
		audio_file.save_audio_file()

		message = {
			"filename": filename
		}
		return jsonify(message), 200
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500


@cross_origin(origin=cors_ip,headers=cors_header)
@files.route("/files/<filename>", methods=['GET'])
def get_text_category_file(filename):
	return "Not Implemented: Get text and category of the file : " + filename


@cross_origin(origin=cors_ip,headers=cors_header)
@files.route("/files/<filename>/text", methods=['GET'])
def get_text_file(filename):
	audiofile = AudioFile()
	voice_text = VoiceText()
	audiofile.filename = filename
	try:
		if audiofile.check_filename_exists():
			voice_text.get_voice_text_from_db(filename)
			if len(voice_text.converted_text) > 0:
				print("The entry is already present")
				message = {
					"text": voice_text.converted_text
				}
				return jsonify(message), 200

			# perform voice to text AWS and store it in DB
			audiofile.get_s3Link()
			# audiofile has s3Link and filename
			voice_text.aws_voice_to_text(audiofile)
			message = {
				"text": voice_text.converted_text
			}
			voice_text.store_voice_text(filename)
			return jsonify(message), 200
		else:
			message = {
				"message": "File not found in out records"
			}
			return jsonify(message), 404
	except:
		message = {
			"message": "Internal Server Error, something went wrong"
		}
		return jsonify(message), 500


@cross_origin(origin=cors_ip,headers=cors_header)
@files.route("/files/<filename>/text", methods=['PUT'])
def update_text_file(filename):
	# try:
		content = request.json
		if content and 'text' not in content:
			print("In here")
			message = {
				"message": "text is not present in the request"
			}
			return jsonify(message), 400

		audio_file = AudioFile()
		audio_file.filename = filename
		if not audio_file.check_filename_exists():
			message = {
				"message": "File not fount in our records"
			}
			return jsonify(message), 404

		voice_text = VoiceText()
		voice_text.converted_text = content['text']
		voice_text.store_voice_text(filename)

		return '', 200
	# except:
	# 	message = {
	# 		"message": "Internal Server Error, something went wrong"
	# 	}
	# 	return jsonify(message), 500

@cross_origin(origin=cors_ip,headers=cors_header)
@files.route("/files/<filename>/categories", methods=['GET'])
def get_category_file(filename):
	return "Not Implemented: Get categories of the file : " + filename



