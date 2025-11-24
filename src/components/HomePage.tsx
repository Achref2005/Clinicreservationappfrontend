import { Link } from 'react-router-dom';
import { Calendar, Clock, Shield, Heart, Award, Users } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

export function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="max-w-3xl">
            <h1 className="text-slate-50 mb-4">
              Your Health, Our Priority
            </h1>
            <p className="text-blue-100 mb-8">
              Experience compassionate care with our team of experienced healthcare professionals. 
              Book your appointment easily and get the medical attention you deserve.
            </p>
            <Link to="/book">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50">
                <Calendar className="w-5 h-5 mr-2" />
                Book Appointment
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-slate-900 mb-3">Why Choose MediCare Clinic?</h2>
            <p className="text-slate-600">Providing exceptional healthcare services to our community</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardContent className="pt-6">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Clock className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-slate-900 mb-2">Easy Scheduling</h3>
                <p className="text-slate-600">
                  Book appointments 24/7 through our convenient system. Get instant confirmation and reminders.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-slate-900 mb-2">Expert Doctors</h3>
                <p className="text-slate-600">
                  Our team consists of highly qualified and experienced medical professionals across all specialties.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-slate-900 mb-2">Quality Care</h3>
                <p className="text-slate-600">
                  We maintain the highest standards of medical care with modern facilities and equipment.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-slate-900 mb-4">About MediCare Clinic</h2>
              <p className="text-slate-600 mb-4">
                With over 25 years of experience, MediCare Clinic has been serving the community 
                with dedication and excellence. We believe in providing personalized care that treats 
                the whole person, not just the symptoms.
              </p>
              <p className="text-slate-600 mb-6">
                Our state-of-the-art facility is equipped with the latest medical technology, 
                and our staff is committed to making your visit comfortable and stress-free.
              </p>
              <div className="grid grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-blue-600 mb-1">25+</div>
                  <div className="text-slate-600">Years Experience</div>
                </div>
                <div className="text-center">
                  <div className="text-blue-600 mb-1">15+</div>
                  <div className="text-slate-600">Specialist Doctors</div>
                </div>
                <div className="text-center">
                  <div className="text-blue-600 mb-1">50k+</div>
                  <div className="text-slate-600">Happy Patients</div>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <CardContent className="pt-6">
                  <Heart className="w-8 h-8 mb-3" />
                  <h3 className="text-white mb-2">Compassionate</h3>
                  <p className="text-blue-100">We care about your wellbeing</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
                <CardContent className="pt-6">
                  <Award className="w-8 h-8 mb-3" />
                  <h3 className="text-white mb-2">Certified</h3>
                  <p className="text-green-100">Accredited healthcare facility</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <CardContent className="pt-6">
                  <Clock className="w-8 h-8 mb-3" />
                  <h3 className="text-white mb-2">Available</h3>
                  <p className="text-purple-100">Extended hours for your convenience</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
                <CardContent className="pt-6">
                  <Shield className="w-8 h-8 mb-3" />
                  <h3 className="text-white mb-2">Trusted</h3>
                  <p className="text-orange-100">Serving the community since 1998</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-white mb-4">Ready to Get Started?</h2>
          <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
            Book your appointment today and experience healthcare the way it should be - 
            personal, professional, and centered around you.
          </p>
          <Link to="/book">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50">
              <Calendar className="w-5 h-5 mr-2" />
              Book Your Appointment
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
