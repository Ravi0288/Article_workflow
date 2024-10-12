import os
import shutil
from django.shortcuts import render
from model.provider import Provider_meta_data_deposit
import pytz
import datetime
from model.archive import Archive
from django.core.files import File


def file_transfer_from_deposites(request):
    context = {
        'heading' : 'Message',
        'message' : 'All File / Directory transferred successfully.'
    }

    succ = True

    due_for_transfer = Provider_meta_data_deposit.objects.filter(
        provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        )

    if not due_for_transfer.exists():
        context['message'] = 'Deposit sync successfully executed. No pending Deposit found for action.'

    else:
        for provs in due_for_transfer:
            source_dir = provs.source
            dest_dir = '/ai/metadata/'

            # Create destination directory if it doesn't exist
            os.makedirs(dest_dir, exist_ok=True)

            if not os.path.exists(source_dir):
                context['message'] = {'error': 'Source directory does not exist.'}

            # # copy from source
            # if provs.operation_type == 'COPY':
            #     try:
            #         # Copy all files and folders from the source directory to the destination directory
            #         shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
            #         context['message'] = {'success': 'Files and folders transferred successfully.'}
            #         succ = True
            #     except Exception as e:
            #         context['message'] = {'error': str(e)}
            #         succ = False

            # move content from source to destination
            # if provs.operation_type == 'MOVE':
            updated = 0
            created = 0
            try:
                # Move all files and folders from the source directory to the destination directory
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_type = file.split('.')[-1]
                        file_size = os.path.getsize(file_path)

                        x = Archive.objects.filter(deposite_path=file_path)
                        
                        # if file already stored update else created new file
                        if x.exists():
                            x = x[0]
                            # check the size of the file, if no changes than pass it, else perform update
                            if x.file_size == file_size:
                                pass
                            else:

                                # update the existing Archive
                                x.file_size = file_size
                                x.is_content_changed = True
                                destination_file_path = x.file_content.path
                                os.remove(destination_file_path)
                                # Copy the new file to the destination path
                                shutil.copy(file_path, destination_file_path)
                                x.save()
                                updated +=1

                        else:
                            # create new Archive
                            x = Archive.objects.create(
                                file_name_on_source = file,
                                provider = provs.provider,
                                processed_on = datetime.datetime.now(tz=pytz.utc),
                                status = 'waiting',
                                file_size = file_size,
                                file_type = file_type,

                                # deposit path will store source address
                                deposite_path = file_path
                            )
                            file_name = str(x.id) + '.' + file.split('.')[-1]
                            with open(file_path, 'rb') as f:
                                x.file_content.save(file_name, File(f))
                            created +=1

                        # os.remove(file_path)
                    
                context['message'] = f'''{created} files created and {updated} files updated successfully.'''
                succ = True
            except Exception as e:
                    context['message'] = {'error': str(e)}
                    succ = False

            # if process executed successfully update the provider record
            if succ: 
                provider = provs.provider
                provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
                provider.status = 'success'
                provider.last_error_message = 'N/A'
                provider.save()

            # if process execution failed update the error message to provider record
            else:
                provider = provs.provider
                provider.status = 'failed'
                provider.last_error_message = context['message']
                provider.save()


    return render(request, 'common/dashboard.html', context=context)