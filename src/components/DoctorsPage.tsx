import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Award, Calendar } from 'lucide-react';
import { Button } from './ui/button';
import { Link } from 'react-router-dom';
import { apiService, Doctor } from '../services/api';
import { toast } from 'sonner@2.0.3';

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
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const data = await apiService.getDoctors();
        setDoctors(data);
      } catch (error) {
        console.error('Error fetching doctors:', error);
        toast.error('Failed to load doctors. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDoctors();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 py-12 flex items-center justify-center">
        <p className="text-slate-600">Loading doctors...</p>
      </div>
    );
  }

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
                    {doctor.name.split(' ').length > 1 ? doctor.name.split(' ')[1][0] : doctor.name[0]}
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
