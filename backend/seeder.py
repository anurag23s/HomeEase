from models import db, Package, Service

def add_packages():
    service = Service.query.get(1)  # Get service with ID 1
    if not service:
        print("Service with ID 1 not found!")
        return

    # Define packages
    package1 = Package(name="AC1", description="Basic", price=800)
    package2 = Package(name="AC2", description="Advanced", price=1200)

    # Link packages to service
    package1.services.append(service)
    package2.services.append(service)

    # Add to DB
    db.session.add_all([package1, package2])
    db.session.commit()
    print("Packages added successfully!")
