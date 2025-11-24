import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Award, Calendar } from 'lucide-react';
import { Button } from './ui/button';
import { Link } from 'react-router-dom';

const doctors = [
  {
    id: 1,
    name: 'Dr. Sarah Johnson',
    specialty: 'Cardiology',
    experience: '15 years',
    qualifications: 'MD, FACC',
    about: 'Specialized in preventive cardiology and heart disease management with a focus on patient education.',
  },
  {
    id: 2,
    name: 'Dr. Michael Chen',
    specialty: 'Pediatrics',
    experience: '12 years',
    qualifications: 'MD, FAAP',
    about: 'Dedicated to providing comprehensive care for children from infancy through adolescence.',
  },
  {
    id: 3,
    name: 'Dr. Emily Rodriguez',
    specialty: 'Dermatology',
    experience: '10 years',
    qualifications: 'MD, FAAD',
    about: 'Expert in medical and cosmetic dermatology with advanced training in skin cancer treatment.',
  },
  {
    id: 4,
    name: 'Dr. James Williams',
    specialty: 'Orthopedics',
    experience: '18 years',
    qualifications: 'MD, FAAOS',
    about: 'Specializes in sports medicine and minimally invasive orthopedic surgery.',
  },
  {
    id: 5,
    name: 'Dr. Lisa Anderson',
    specialty: 'Internal Medicine',
    experience: '14 years',
    qualifications: 'MD, FACP',
    about: 'Focused on adult medicine, chronic disease management, and preventive healthcare.',
  },
  {
    id: 6,
    name: 'Dr. David Kumar',
    specialty: 'Neurology',
    experience: '16 years',
    qualifications: 'MD, PhD, FAAN',
    about: 'Expert in treating neurological disorders including migraines, epilepsy, and movement disorders.',
  },
  {
    id: 7,
    name: 'Dr. Rachel Thompson',
    specialty: 'Obstetrics & Gynecology',
    experience: '11 years',
    qualifications: 'MD, FACOG',
    about: 'Provides comprehensive women\'s healthcare including prenatal care and minimally invasive surgery.',
  },
  {
    id: 8,
    name: 'Dr. Robert Martinez',
    specialty: 'Psychiatry',
    experience: '13 years',
    qualifications: 'MD, FAPA',
    about: 'Specializes in mood disorders, anxiety, and integrative mental health treatment approaches.',
  },
];

const specialtyColors: { [key: string]: string } = {
  'Cardiology': 'bg-red-100 text-red-700',
  'Pediatrics': 'bg-blue-100 text-blue-700',
  'Dermatology': 'bg-pink-100 text-pink-700',
  'Orthopedics': 'bg-green-100 text-green-700',
  'Internal Medicine': 'bg-purple-100 text-purple-700',
  'Neurology': 'bg-indigo-100 text-indigo-700',
  'Obstetrics & Gynecology': 'bg-rose-100 text-rose-700',
  'Psychiatry': 'bg-teal-100 text-teal-700',
};

export function DoctorsPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-slate-900 mb-3">Our Medical Team</h1>
          <p className="text-slate-600 max-w-2xl mx-auto">
            Meet our dedicated team of healthcare professionals committed to providing 
            you with the highest quality medical care.
          </p>
        </div>

        {/* Doctors Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {doctors.map((doctor) => (
            <Card key={doctor.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-xl">
                    {doctor.name.split(' ')[1][0]}
                  </div>
                  <Badge className={specialtyColors[doctor.specialty] || 'bg-slate-100 text-slate-700'}>
                    {doctor.specialty}
                  </Badge>
                </div>
                <h3 className="text-slate-900">{doctor.name}</h3>
                <p className="text-slate-500">{doctor.qualifications}</p>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-slate-600 mb-3">
                  <Award className="w-4 h-4" />
                  <span>{doctor.experience} of experience</span>
                </div>
                <p className="text-slate-600 mb-4">{doctor.about}</p>
                <Link to="/book">
                  <Button variant="outline" className="w-full">
                    <Calendar className="w-4 h-4 mr-2" />
                    Book Appointment
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* CTA */}
        <Card className="bg-gradient-to-br from-blue-600 to-blue-800 text-white">
          <CardContent className="pt-6 text-center">
            <h2 className="text-white mb-3">Ready to Schedule Your Visit?</h2>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Our team is here to help you with all your healthcare needs. Book an appointment today 
              and experience personalized medical care.
            </p>
            <Link to="/book">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50">
                <Calendar className="w-5 h-5 mr-2" />
                Book Now
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
