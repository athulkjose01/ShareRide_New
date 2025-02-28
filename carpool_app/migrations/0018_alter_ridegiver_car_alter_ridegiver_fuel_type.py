# Generated by Django 4.2.11 on 2025-01-26 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carpool_app', '0017_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ridegiver',
            name='car',
            field=models.CharField(choices=[('Maruti Suzuki Alto', 'Maruti Suzuki Alto'), ('Maruti Suzuki Wagon R', 'Maruti Suzuki Wagon R'), ('Maruti Suzuki Swift', 'Maruti Suzuki Swift'), ('Maruti Suzuki Dzire', 'Maruti Suzuki Dzire'), ('Maruti Suzuki Baleno', 'Maruti Suzuki Baleno'), ('Maruti Suzuki Brezza', 'Maruti Suzuki Brezza'), ('Maruti Suzuki Grand Vitara', 'Maruti Suzuki Grand Vitara'), ('Maruti Suzuki Ciaz', 'Maruti Suzuki Ciaz'), ('Maruti Suzuki XL6', 'Maruti Suzuki XL6'), ('Maruti Suzuki Eeco', 'Maruti Suzuki Eeco'), ('Maruti Suzuki Fronx', 'Maruti Suzuki Fronx'), ('Maruti Suzuki Maruti 800', 'Maruti Suzuki Maruti 800'), ('Maruti Suzuki Ignis', 'Maruti Suzuki Ignis'), ('Hyundai Grand i10 Nios', 'Hyundai Grand i10 Nios'), ('Hyundai i20', 'Hyundai i20'), ('Hyundai Creta', 'Hyundai Creta'), ('Hyundai Venue', 'Hyundai Venue'), ('Hyundai Verna', 'Hyundai Verna'), ('Hyundai Alcazar', 'Hyundai Alcazar'), ('Hyundai Kona Electric', 'Hyundai Kona Electric'), ('Hyundai Exter', 'Hyundai Exter'), ('Hyundai Tucson', 'Hyundai Tucson'), ('Hyundai Ioniq 5', 'Hyundai Ioniq 5'), ('Kia Seltos', 'Kia Seltos'), ('Kia Carens', 'Kia Carens'), ('Kia Sonet', 'Kia Sonet'), ('Kia EV6', 'Kia EV6'), ('Kia Carnival', 'Kia Carnival'), ('Kia Sportage', 'Kia Sportage'), ('Tata Nexon', 'Tata Nexon'), ('Tata Punch', 'Tata Punch'), ('Tata Tiago', 'Tata Tiago'), ('Tata Harrier', 'Tata Harrier'), ('Tata Safari', 'Tata Safari'), ('Tata Nexon EV', 'Tata Nexon EV'), ('Tata Altroz', 'Tata Altroz'), ('Tata Tigor EV', 'Tata Tigor EV'), ('Tata Hexa', 'Tata Hexa'), ('Mahindra Scorpio', 'Mahindra Scorpio'), ('Mahindra Thar', 'Mahindra Thar'), ('Mahindra XUV700', 'Mahindra XUV700'), ('Mahindra Bolero', 'Mahindra Bolero'), ('Mahindra XUV300', 'Mahindra XUV300'), ('Mahindra XUV400 EV', 'Mahindra XUV400 EV'), ('Mahindra Marazzo', 'Mahindra Marazzo'), ('Toyota Fortuner', 'Toyota Fortuner'), ('Toyota Innova Crysta', 'Toyota Innova Crysta'), ('Toyota Camry', 'Toyota Camry'), ('Toyota Corolla Altis', 'Toyota Corolla Altis'), ('Toyota Hilux', 'Toyota Hilux'), ('Toyota Vellfire', 'Toyota Vellfire'), ('Toyota Urban Cruiser Hyryder', 'Toyota Urban Cruiser Hyryder'), ('Honda City', 'Honda City'), ('Honda Amaze', 'Honda Amaze'), ('Honda WR-V', 'Honda WR-V'), ('Honda Civic', 'Honda Civic'), ('Honda BR-V', 'Honda BR-V'), ('Renault Kwid', 'Renault Kwid'), ('Renault Triber', 'Renault Triber'), ('Renault Kiger', 'Renault Kiger'), ('Skoda Kushaq', 'Skoda Kushaq'), ('Skoda Slavia', 'Skoda Slavia'), ('Skoda Octavia', 'Skoda Octavia'), ('Skoda Superb', 'Skoda Superb'), ('Volkswagen Taigun', 'Volkswagen Taigun'), ('Volkswagen Polo', 'Volkswagen Polo'), ('Volkswagen Tiguan', 'Volkswagen Tiguan'), ('Volkswagen Virtus', 'Volkswagen Virtus'), ('Mercedes-Benz C-Class', 'Mercedes-Benz C-Class'), ('Mercedes-Benz E-Class', 'Mercedes-Benz E-Class'), ('Mercedes-Benz GLS', 'Mercedes-Benz GLS'), ('Mercedes-Benz G-Class', 'Mercedes-Benz G-Class'), ('BMW 3 Series', 'BMW 3 Series'), ('BMW X1', 'BMW X1'), ('BMW X5', 'BMW X5'), ('Audi Q3', 'Audi Q3'), ('Audi A8 L', 'Audi A8 L'), ('Volvo XC40', 'Volvo XC40'), ('Jaguar F-Pace', 'Jaguar F-Pace'), ('Land Rover Discovery Sport', 'Land Rover Discovery Sport'), ('Land Rover Defender', 'Land Rover Defender'), ('Jeep Compass', 'Jeep Compass'), ('Jeep Grand Cherokee', 'Jeep Grand Cherokee'), ('Lexus RX 500h', 'Lexus RX 500h'), ('Porsche Macan', 'Porsche Macan'), ('Ferrari Roma', 'Ferrari Roma'), ('Lamborghini Urus', 'Lamborghini Urus'), ('Rolls-Royce Ghost', 'Rolls-Royce Ghost'), ('Nissan Magnite', 'Nissan Magnite'), ('Nissan Terrano', 'Nissan Terrano'), ('MG Hector', 'MG Hector'), ('MG ZS EV', 'MG ZS EV'), ('BYD Atto 3', 'BYD Atto 3'), ('Mini Cooper SE', 'Mini Cooper SE'), ('Mitsubishi Pajero Sport', 'Mitsubishi Pajero Sport'), ('Isuzu D-Max V-Cross', 'Isuzu D-Max V-Cross'), ('Fiat Punto', 'Fiat Punto'), ('Fiat Linea', 'Fiat Linea'), ('Fiat Abarth Punto', 'Fiat Abarth Punto'), ('Fiat Urban Cross', 'Fiat Urban Cross'), ('Fiat Avventura', 'Fiat Avventura'), ('Fiat 500', 'Fiat 500'), ('Ford EcoSport', 'Ford EcoSport'), ('Maruti Suzuki Defender', 'Maruti Suzuki Defender'), ('Hyundai Getz', 'Hyundai Getz'), ('Nissan Micra', 'Nissan Micra'), ('Nissan Sunny', 'Nissan Sunny'), ('Nissan Kicks', 'Nissan Kicks'), ('Nissan GT-R', 'Nissan GT-R'), ('Nissan X-Trail', 'Nissan X-Trail'), ('Nissan Leaf', 'Nissan Leaf'), ('Nissan Patrol', 'Nissan Patrol'), ('Nissan Terra', 'Nissan Terra'), ('Nissan Compact MPV', 'Nissan Compact MPV'), ('Nissan Compact SUV', 'Nissan Compact SUV')], max_length=50),
        ),
        migrations.AlterField(
            model_name='ridegiver',
            name='fuel_type',
            field=models.CharField(choices=[('petrol', 'petrol'), ('diesel', 'diesel'), ('ev', 'ev'), ('hybrid', 'hybrid')], default='Petrol', max_length=20),
        ),
    ]
