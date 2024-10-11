import os
import shutil
from django.shortcuts import render
from model.provider import Provider_meta_data_deposit
import pytz
import datetime

def file_transfer_from_deposites(request):
    context = {
        'heading' : 'Message',
        'message' : 'All File / Directory transferred successfully.'
    }

    succ = True

    due_for_transfer = Provider_meta_data_deposit.objects.filter(
        provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc), 
        )

    if not due_for_transfer.count():
        context['message'] = 'No action pending for Deposits'

    for provs in due_for_transfer:
        source_dir = provs.source
        dest_dir = provs.destination

        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)

        if not os.path.exists(source_dir):
            context['message'] = {'error': 'Source directory does not exist.'}

        # copy from source
        if provs.operation_type == 'COPY':
            try:
                # Copy all files and folders from the source directory to the destination directory
                shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                context['message'] = {'success': 'Files and folders transferred successfully.'}
                succ = True
            except Exception as e:
                context['message'] = {'error': str(e)}
                succ = False

        # move content from source to destination
        if provs.operation_type == 'MOVE':
            try:
                # Move all files and folders from the source directory to the destination directory
                for item in os.listdir(source_dir):
                    s = os.path.join(source_dir, item)
                    d = os.path.join(dest_dir, item)
                    shutil.move(s, d)  # Move each item

                    context['message'] = {'success': 'Files and folders transferred successfully.'}
                    succ = True
            except Exception as e:
                    context['message'] = {'error': str(e)}
                    succ = False

        if succ:
            provider = provs.provider
            provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
            provider.status = 'success'
            provider.last_error_message = 'N/A'
            provider.save()
            succ.append(provs.provider.official_name)

        else:
            provider = provs.provider
            provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
            provider.status = 'success'
            provider.last_error_message = context['message']
            provider.save()
            succ.append(provs.provider.official_name)


    return render(request, 'common/dashboard.html', context=context)



