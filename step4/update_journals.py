import srupymarc
import pymarc
import datetime
import warnings
import logging

from model.journal import Journal

def pymarc_field_or_none_str(record, field, subfield1=None, subfield2=None):
    if subfield1 and subfield2:
        try:
            return record[field][subfield1][subfield2]
        except KeyError:
            return "none"
    elif subfield1:
        try:
            return record[field][subfield1]
        except KeyError:
            return "none"
    else:
        try:
            return record[field]
        except KeyError:
            return "none"

def pymarc_field_or_none(record, field, subfield1=None, subfield2=None):
    if subfield1 and subfield2:
        try:
            return record[field][subfield1][subfield2]
        except KeyError:
            return None
    elif subfield1:
        try:
            return record[field][subfield1]
        except KeyError:
            return None
    else:
        try:
            return record[field]
        except KeyError:
            return None

def extract_doi(record):
    for field in record.get_fields("024"):
        if field.get_subfields("2") == ["doi"]:
            return field.get_subfields("a")[0]
    return "none"

def extract_subject_cluster(record):
    subject_cluster = "none"
    for field in record.get_fields("902"):
        if field.get_subfields("b"):
            subject_cluster = field.get_subfields("b")[0]
    if subject_cluster.lower() == "unassigned":
            subject_cluster = "none"
    return subject_cluster

# Function to update the journal model based on the last pull date.
# This function pulls journal records from Alma based using srupymarc and creates one journal entry for each ISSN identified in the journal record.

def update_journal_model(last_pull_date):
    logger = logging.getLogger("journal_logger")
    logger.info(
        f"Running update_journal_model on {datetime.datetime.now().strftime('%Y-%m-%d')}, pulling records since {last_pull_date}"
    )

    valid_collection_statuses = ['pending', 'accepted', 'from_submission', 'rejected']

    if isinstance(last_pull_date, datetime.datetime):
        last_pull_date = last_pull_date.strftime('%Y%m%d')

    query = 'alma.local_field_912="Journal" and mms_modificationDate>"{}"'.format(last_pull_date)
    params = {
        "url": "https://na91.alma.exlibrisgroup.com/view/sru/01NAL_INST",
        "query": query
    }
    journals = Journal.objects.all()
    pymarc_journal_records = srupymarc.searchretrieve(**params)

    for record in pymarc_journal_records:
        p_issn = pymarc_field_or_none(record, '022', 'a')
        e_issn = pymarc_field_or_none(record, '022', 'l')
        if e_issn is None and p_issn is None:
            logger.warning(f"No issn for record with mmsid: {record['001'].data}")
            continue

        # Extract nal_journal_id field. If DNE, reject record with a warning
        nal_journal_id = pymarc_field_or_none_str(record, '900', 'a')
        if nal_journal_id == "none":
            logger.warning(f"No nal_journal_id for record with mmsid: {record['001'].data}")
            continue

        # Check if journal model entries with these ISSNs already exists
        if p_issn:
            journal_match_p_issn = journals.filter(issn=p_issn).first()
        if e_issn:
            journal_match_e_issn = journals.filter(issn=e_issn).first()

        if p_issn == e_issn:
            e_issn = None

        # If the record already exists, update the journal model based on the new record pulled
        if e_issn and journal_match_e_issn:

            title = pymarc_field_or_none_str(record, '245', 'a')
            if title == "none":
                logger.warning(f"No title for record with mmsid: {record['001'].data}")
            journal_match_e_issn.journal_title = title
            journal_match_e_issn.publisher = pymarc_field_or_none_str(record, '260', 'b')

            collection_status = pymarc_field_or_none_str(record, '901', 'a')
            collection_status=collection_status.lower()
            if collection_status not in valid_collection_statuses:
                collection_status = "pending"

            journal_match_e_issn.collection_status = collection_status
            journal_match_e_issn.harvest_source = pymarc_field_or_none_str(record, '918', 'a')
            journal_match_e_issn.nal_journal_id = pymarc_field_or_none_str(record, '900', 'a')
            journal_match_e_issn.mmsid = record['001'].data
            journal_match_e_issn.last_updated = datetime.datetime.now().strftime('%Y%m%d')
            journal_match_e_issn.subject_cluster = extract_subject_cluster(record)
            journal_match_e_issn.requirement_override = pymarc_field_or_none_str(record, '597', 'a')
            journal_match_e_issn.doi=extract_doi(record)
            journal_match_e_issn.save()

        if p_issn and journal_match_p_issn:

            title = pymarc_field_or_none_str(record, '245', 'a')
            if title == "none":
                logger.warning(f"No title for record with mmsid: {record['001'].data}")

            journal_match_p_issn.journal_title = title
            journal_match_p_issn.publisher = pymarc_field_or_none_str(record, '260', 'b')

            collection_status = pymarc_field_or_none_str(record, '901', 'a')
            collection_status=collection_status.lower()
            if collection_status not in valid_collection_statuses:
                collection_status = "pending"

            journal_match_p_issn.collection_status = collection_status
            journal_match_p_issn.harvest_source = pymarc_field_or_none_str(record, '918', 'a')
            journal_match_p_issn.nal_journal_id = pymarc_field_or_none_str(record, '900', 'a')
            journal_match_p_issn.mmsid = record['001'].data
            journal_match_p_issn.last_updated = datetime.datetime.now().strftime('%Y%m%d')
            journal_match_p_issn.subject_cluster = extract_subject_cluster(record)
            journal_match_p_issn.requirement_override = pymarc_field_or_none_str(record, '597', 'a')
            journal_match_p_issn.doi = extract_doi(record)
            journal_match_p_issn.save()

        # If the record does not exist, create a new journal model based on the new record pulled
        if e_issn and not journal_match_e_issn:

            collection_status = pymarc_field_or_none_str(record, '901', 'a')
            collection_status = collection_status.lower()
            if collection_status not in valid_collection_statuses:
                collection_status = "pending"

            title = pymarc_field_or_none_str(record, '245', 'a')
            if title == "none":
                logger.warning(f"No title for record with mmsid: {record['001'].data}")

            new_journal = Journal.objects.create(
                journal_title=title,
                publisher=pymarc_field_or_none_str(record, '260', 'b'),
                issn=e_issn,
                collection_status=collection_status,
                harvest_source=pymarc_field_or_none_str(record, '918', 'a'),
                nal_journal_id=pymarc_field_or_none_str(record, '900', 'a'),
                mmsid=record['001'].data,
                subject_cluster = extract_subject_cluster(record),
                requirement_override = pymarc_field_or_none_str(record, '597', 'a'),
                last_updated = datetime.datetime.now().strftime('%Y%m%d'),
                doi = extract_doi(record)
            )
            new_journal.save()

        if p_issn and not journal_match_p_issn:

            collection_status = pymarc_field_or_none_str(record, '901', 'a')
            collection_status = collection_status.lower()
            if collection_status not in valid_collection_statuses:
                collection_status = "pending"

            title = pymarc_field_or_none_str(record, '245', 'a')
            if title == "none":
                logger.warning(f"No title for record with mmsid: {record['001'].data}")

            new_journal = Journal.objects.create(
                journal_title=title,
                publisher=pymarc_field_or_none_str(record, '260', 'b'),
                issn=p_issn,
                collection_status=collection_status,
                harvest_source=pymarc_field_or_none_str(record, '918', 'a'),
                nal_journal_id=pymarc_field_or_none_str(record, '900', 'a'),
                mmsid=record['001'].data,
                subject_cluster=extract_subject_cluster(record),
                requirement_override=pymarc_field_or_none_str(record, '597', 'a'),
                last_updated=datetime.datetime.now().strftime('%Y%m%d'),
                doi=extract_doi(record)
            )
            new_journal.save()