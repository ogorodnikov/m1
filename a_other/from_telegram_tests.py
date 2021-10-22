    # @pytest.mark.skipif(should_skip, reason="No environment variables configured")
    
    # json_string = r'{"message_id": 1, "from": {"id": 1, "is_bot": false, "first_name": "Test", "username": "User", "language_code": "en"}, "chat": {"id": 221192775, "title": "123", "type": "supergroup"}, "date": 1594068909, "sticker": {"width": 368, "height": 368, "emoji": "🤖", "set_name": "ipuryapack", "is_animated": false, "thumb": {"file_id": "AAMCBAADHQJOFL7mAAJUMF8Dj62hpmDhpRAYvkc8CtIqipolAAJ8AAPA-8cF9yxjgjkLS97A0D4iXQARtQAHbQADHy4AAhoE", "file_unique_id": "AQADwNA-Il0AAx8uAAI", "file_size": 7776, "width": 60, "height": 60}, "file_id": "CAACAgQAAx0CThS-5gACVDBfA4-toaZg4aUQGL5HWerSKoqaJQACArADwPvHBfcsY4I5C3feGgQ", "file_unique_id": "AgADfAADsPvHWQ", "file_size": 14602}}'

    # json_string = r'{"message_id": 1, "from": {"id": 1, "is_bot": false, "first_name": "Test User"}, "chat": {"id": 221192775, "type": "private"}, "date": 1, "sticker": {"width": 368, "height": 368, "is_animated": false, "file_id": "CAACAgIAAxkBAAIF6GES9nEyKUKbGVt4XFzpjOeYv09dAAIUAAPp2BMo6LwZ1x6IhdYgBA", "file_unique_id": "1"}}'

    # sticker_message = types.Message.de_json(json_string)