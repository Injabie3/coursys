from courselib.auth import requires_role
from .models import SessionalAccount, SessionalContract, SessionalConfig
from .forms import SessionalAccountForm, SessionalContractForm, SessionalConfigForm, SessionalAttachmentForm
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.db import transaction
from log.models import LogEntry
from coredata.models import AnyPerson, Role, Person
from dashboard.letters import sessional_form
import csv, datetime


@requires_role(["TAAD", "GRAD", "ADMN"])
def sessionals_index(request):
    sessionals = SessionalContract.objects.visible(request.units)
    return render(request, 'sessionals/index.html', {'sessionals': sessionals})


@requires_role(["TAAD", "GRAD", "ADMN"])
def download_sessionals(request):
    sessionals = SessionalContract.objects.visible(request.units)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'inline; filename="sessionals-%s.csv"' % \
                                      datetime.datetime.now().strftime('%Y%m%d')
    writer = csv.writer(response)
    writer.writerow(['Name', 'Account', 'Unit', 'SIN', 'Appointment Start', 'Appointment End', 'Pay Start', 'Pay End',
                     'Offering', 'Course Hours Breakdown', 'Appointment Guarantee', 'Appointment Type',
                     'Weekly Contact Hours', 'Total Salary', 'Notes'])
    for s in sessionals:
        writer.writerow([s.sessional.get_person(), s.account, s.unit, s.sin, s.appointment_start, s.appointment_end,
                         s.pay_start, s.pay_end, s.offering, s.course_hours_breakdown, s.get_appt_guarantee_display(),
                         s.get_appt_type_display(), s.contact_hours, s.total_salary, s.notes])
    return response


@requires_role(["TAAD", "GRAD", "ADMN"])
def manage_accounts(request):
    accounts = SessionalAccount.objects.visible(request.units)
    return render(request, 'sessionals/manage_accounts.html', {'accounts': accounts})


@requires_role(["TAAD", "GRAD", "ADMN"])
def new_account(request):
    if request.method == 'POST':
        form = SessionalAccountForm(request, request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Account was created.'
                                 )
            l = LogEntry(userid=request.user.username,
                         description="added account: %s" % account,
                         related_object=account
                         )
            l.save()

            return HttpResponseRedirect(reverse('sessionals:manage_accounts'))
    else:
        form = SessionalAccountForm(request)
    return render(request, 'sessionals/new_account.html', {'form': form})


@requires_role(["TAAD", "GRAD", "ADMN"])
def edit_account(request, account_slug):
    account = get_object_or_404(SessionalAccount, slug=account_slug, unit__in=request.units)
    if request.method == 'POST':
        form = SessionalAccountForm(request, request.POST, instance=account)
        if form.is_valid():
            account = form.save(commit=False)
            account.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Account was edited.'
                                 )
            l = LogEntry(userid=request.user.username,
                         description="edited account: %s" % account,
                         related_object=account
                         )
            l.save()
            return HttpResponseRedirect(reverse('sessionals:manage_accounts'))
    else:
        form = SessionalAccountForm(request, instance=account)
    return render(request, 'sessionals/edit_account.html', {'form': form, 'account': account})


@requires_role(["TAAD", "GRAD", "ADMN"])
def delete_account(request, account_id):
    account = get_object_or_404(SessionalAccount, id=account_id, unit__in=request.units)
    if request.method == 'POST':
        account.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Account was deleted.'
                             )
        l = LogEntry(userid=request.user.username,
                     description="deleted account: %s" % account,
                     related_object=account
                     )
        l.save()
    return HttpResponseRedirect(reverse('sessionals:manage_accounts'))


@requires_role(["TAAD", "GRAD", "ADMN"])
def view_account(request, account_slug):
    account = get_object_or_404(SessionalAccount, slug=account_slug, unit__in=request.units)
    return render(request, 'sessionals/view_account.html', {'account': account})


@requires_role(["TAAD", "GRAD", "ADMN"])
def manage_configs(request):
    configs = SessionalConfig.objects.filter(unit__in=request.units)
    #  Sysadmins may manage multiple units.  We'll make sure they always see the "new config" action.  Others
    #  presumably all only admin one single unit, so should only see that link if they don't already have a default
    #  config, since it has a one-to-one relationship with the unit.
    is_admin = Role.objects_fresh.filter(person__userid=request.user.username, role='SYSA').count() > 0
    return render(request, 'sessionals/manage_configs.html', {'configs': configs, 'is_admin': is_admin})


@requires_role(["TAAD", "GRAD", "ADMN"])
def new_config(request):
    if request.method == 'POST':
        form = SessionalConfigForm(request, request.POST)
        if form.is_valid():
            config = form.save(commit=False)
            config.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Configuration was created.'
                                 )
            l = LogEntry(userid=request.user.username,
                         description="added config: %s" % config,
                         related_object=config
                         )
            l.save()

            return HttpResponseRedirect(reverse('sessionals:manage_configs'))
    else:
        form = SessionalConfigForm(request)
    return render(request, 'sessionals/new_config.html', {'form': form})


@requires_role(["TAAD", "GRAD", "ADMN"])
def edit_config(request, config_slug):
    config = get_object_or_404(SessionalConfig, slug=config_slug, unit__in=request.units)
    if request.method == 'POST':
        form = SessionalConfigForm(request, request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Configuration was edited.'
                                 )
            l = LogEntry(userid=request.user.username,
                         description="edited config: %s" % config,
                         related_object=config
                         )
            l.save()
            return HttpResponseRedirect(reverse('sessionals:manage_configs'))
    else:
        form = SessionalConfigForm(request, instance=config)
    return render(request, 'sessionals/edit_config.html', {'form': form, 'config': config})


@requires_role(["TAAD", "GRAD", "ADMN"])
def new_contract(request):
    if request.method == 'POST':
        form = SessionalContractForm(request, request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            # Let's convert the person in there to an AnyPerson
            person = form.cleaned_data['person']
            contract.sessional = AnyPerson.get_or_create_for(person=person)
            contract.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Contract was created.'
                                 )
            l = LogEntry(userid=request.user.username,
                         description="added sessional contract for: %s" % contract.sessional,
                         related_object=contract
                         )
            l.save()

            return HttpResponseRedirect(reverse('sessionals:sessionals_index'))
    else:
        form = SessionalContractForm(request)
        #  Everyone except a sysadmin most likely has only one unit they have admin roles for.  Let's try to
        #  find the config matching that unit, and if it exists, use it for default values.
        config = SessionalConfig.objects.filter(unit__in=request.units).first()
        if config:
            form.fields['appointment_start'].initial = config.appointment_start
            form.fields['appointment_end'].initial = config.appointment_end
            form.fields['pay_start'].initial = config.pay_start
            form.fields['pay_end'].initial = config.pay_end
            form.fields['course_hours_breakdown'].initial = config.course_hours_breakdown
    return render(request, 'sessionals/new_contract.html', {'form': form})


@requires_role(["TAAD", "GRAD", "ADMN"])
def edit_contract(request, contract_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    if request.method == 'POST':
        form = SessionalContractForm(request, request.POST, instance=contract)
        if form.is_valid():
            contract = form.save(commit=False)
            # Let's convert the person in there to an AnyPerson
            person = form.cleaned_data['person']
            contract.sessional = AnyPerson.get_or_create_for(person=person)
            contract.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Contract was edited.'
                                 )
            l = LogEntry(userid=request.user.username,
                         description="edited sessional contract for: %s" % contract.sessional,
                         related_object=contract
                         )
            l.save()

            return HttpResponseRedirect(reverse('sessionals:sessionals_index'))
    else:
        form = SessionalContractForm(request, instance=contract)
        form.fields['person'].initial = contract.sessional.get_person().emplid
    return render(request, 'sessionals/edit_contract.html', {'form': form, 'contract': contract})


@requires_role(["TAAD", "GRAD", "ADMN"])
def delete_contract(request, contract_id):
    contract = get_object_or_404(SessionalContract, pk=contract_id, unit__in=request.units)
    if request.method == 'POST':
        contract.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Contract was deleted.'
                             )
        l = LogEntry(userid=request.user.username,
                     description="deleted sessional contract: %s" % contract,
                     related_object=contract
                     )
        l.save()
    return HttpResponseRedirect(reverse('sessionals:sessionals_index'))


@requires_role(["TAAD", "GRAD", "ADMN"])
def print_contract(request, contract_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    # If no one has ever checked the 'I've verified the visa info for this person'
    # box, let's stop them from printing.  We don't want to send this anywhere, but
    # it's just for our own peace of mind.
    if not contract.visa_verified:
            messages.error(request, 'You must verify the sessional\'s visa information before printing')
            return HttpResponseRedirect(reverse('sessionals:view_contract',
                                                kwargs={'contract_slug': contract_slug}))
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="sessionalform.pdf"'
    sessional_form(contract, response)
    return response


@requires_role(["TAAD", "GRAD", "ADMN"])
def view_contract(request, contract_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    return render(request, 'sessionals/view_contract.html', {'contract': contract})


@requires_role(["TAAD", "GRAD", "ADMN"])
@transaction.atomic
def new_attachment(request, contract_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    editor = get_object_or_404(Person, userid=request.user.username)

    form = SessionalAttachmentForm()
    context = {"contract": contract,
               "attachment_form": form}

    if request.method == "POST":
        form = SessionalAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.sessional = contract
            attachment.created_by = editor
            upfile = request.FILES['contents']
            filetype = upfile.content_type
            if upfile.charset:
                filetype += "; charset=" + upfile.charset
            attachment.mediatype = filetype
            attachment.save()
            return HttpResponseRedirect(reverse('sessionals:view_contract', kwargs={'contract_slug': contract.slug}))
        else:
            context.update({"attachment_form": form})

    return render(request, 'sessionals/add_attachment.html', context)


@requires_role(["TAAD", "GRAD", "ADMN"])
def view_attachment(request, contract_slug, attach_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    attachment = get_object_or_404(contract.attachments.all(), slug=attach_slug)
    filename = attachment.contents.name.rsplit('/')[-1]
    resp = StreamingHttpResponse(attachment.contents.chunks(), content_type=attachment.mediatype)
    resp['Content-Disposition'] = 'inline; filename="' + filename + '"'
    resp['Content-Length'] = attachment.contents.size
    return resp


@requires_role(["TAAD", "GRAD", "ADMN"])
def download_attachment(request, contract_slug, attach_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    attachment = get_object_or_404(contract.attachments.all(), slug=attach_slug)
    filename = attachment.contents.name.rsplit('/')[-1]
    resp = StreamingHttpResponse(attachment.contents.chunks(), content_type=attachment.mediatype)
    resp['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    resp['Content-Length'] = attachment.contents.size
    return resp


@requires_role(["TAAD", "GRAD", "ADMN"])
def delete_attachment(request, contract_slug, attach_slug):
    contract = get_object_or_404(SessionalContract, slug=contract_slug, unit__in=request.units)
    attachment = get_object_or_404(contract.attachments.all(), slug=attach_slug)
    attachment.hide()
    messages.add_message(request,
                         messages.SUCCESS,
                         'Attachment deleted.'
                         )
    l = LogEntry(userid=request.user.username, description="Hid attachment %s" % attachment, related_object=attachment)
    l.save()
    return HttpResponseRedirect(reverse('sessionals:view_contract', kwargs={'contract_slug': contract.slug}))
