@app.route('/download')
def download():
    
    task_id = request.args.get('task_id')
    content = request.args.get('content')
    as_attachment = request.args.get('as_attachment', False)
    
    if content == 'statevector':
        
        path = app.static_folder + "/figures/"
        filename = f"bloch_multivector_task_{task_id}.png"
        
        figure_path = path + filename
        
        print(f"ROUTES path {path}")
        print(f"ROUTES filename {filename}")
        print(f"ROUTES figure_path {figure_path}")
        
        runner.download_figure_from_s3(filename)
        
        import os
        import io
        from flask import send_file
        
        stream = io.BytesIO()
        
        with open(figure_path, 'rb') as figure_open:
            stream.write(figure_open.read())

        stream.seek(0)

        os.remove(figure_path)

        return send_file(
            stream, 
            mimetype='image/png', 
            attachment_filename=filename,
            as_attachment=as_attachment
            )
                     
      
                     
        
        # try:
        
        #     return send_from_directory(path, filename, as_attachment=as_attachment)
            
        # finally:
            
        #     print(f"ROUTES remove figure_path {figure_path}")
        #     os.remove(figure_path)
            
            
            
            
            
        
        # presigned_url = runner.get_figure_presigned_url(filename)
        # return presigned_url
        # redirect(presigned_url)
        
        # stream = runner.stream_figure_from_s3(filename)
        # print(f"ROUTES stream: {stream}")
        # return send_from_directory(path, stream, as_attachment=as_attachment)
        
        # return send_from_directory(path, filename, as_attachment=as_attachment)
        
    return ''
        
    # return redirect(request.referrer or url_for('home'))
    
    
    
    
    
    
    
     def move_figure_to_s3(self, from_path, to_path):
        
        import boto3
        
        s3_resource = boto3.resource("s3")
        core_bucket = s3_resource.Bucket("m1-core-bucket")
        
        core_bucket.upload_file(
            from_path, 
            to_path, 
            ExtraArgs={"ACL": "private", "ContentType": "image/png"}
        )
        
        os.remove(from_path)
        
        
    def download_figure_from_s3(self, filename):
        
        import boto3
        
        s3_resource = boto3.resource("s3")
        core_bucket = s3_resource.Bucket("m1-core-bucket")
        
        from_path = "figures/" + filename
        to_path = self.static_folder + '/figures/' + filename
        
        print(f"RUNNER download_figure_from_s3 - from_path {from_path}")
        print(f"RUNNER download_figure_from_s3 - to_path {to_path}")
        
        core_bucket.download_file(
            from_path, 
            to_path
        )
        
    
    def stream_figure_from_s3(self, filename):
        
        import io
        import boto3
        
        stream = io.BytesIO()
        
        s3_resource = boto3.resource("s3")
        core_bucket = s3_resource.Bucket("m1-core-bucket")
        
        from_path = "figures/" + filename
        
        print(f"RUNNER from_path {from_path}")
        
        core_bucket.download_fileobj(
            from_path, 
            stream
        )
        
        return stream
        
    
    def get_figure_presigned_url(self, filename):

        import boto3
        
        s3_client = boto3.client("s3")
        
        from_path = "figures/" + filename

        presigned_url = s3_client.generate_presigned_url(
            'get_object', 
            Params = {
                'Bucket': 'm1-core-bucket', 
                'Key': from_path
            }, 
            ExpiresIn = 100
        )

        print(f"RUNNER presigned_url {presigned_url}")
        
        return presigned_url