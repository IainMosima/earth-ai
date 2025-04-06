import logging

from app.models import Company
from scripts.data.seed_data import companies

logger = logging.getLogger(__name__)



def seed_companies():
    try:
        # Check if companies already exist
        count = Company.objects.count()
        
        if count == 0:
            logger.info("No companies found in database. Seeding initial data...")
            
            # Insert all companies from seed data
            for company_data in companies:
                company = Company(**company_data)
                company.save()
            
            logger.info(f"Successfully seeded {len(companies)} companies into the database.")
        else:
            logger.info(f"Database already contains {count} companies. Skipping seed.")
    except Exception as error:
        logger.error(f"Error seeding companies: {str(error)}")
