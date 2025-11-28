import { useState } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Calendar, Clock, User, AlertCircle } from 'lucide-react';
import { apiService, Appointment } from '../services/api';
import { toast } from 'sonner@2.0.3';

export function AppointmentsPage() {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [searched, setSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Search by phone if provided, otherwise by name
      const data = await apiService.getAppointments(phone || undefined);
      
      // Filter by name if provided
      let filtered = data;
      if (name) {
        filtered = data.filter((apt) =>
          apt.patient_name.toLowerCase().includes(name.toLowerCase())
        );
      }
      
      setAppointments(filtered);
      setSearched(true);
      
      if (filtered.length === 0) {
        toast.info('No appointments found for the provided information.');
      }
    } catch (error) {
      console.error('Error fetching appointments:', error);
      toast.error('Failed to fetch appointments. Please try again.');
      setAppointments([]);
      setSearched(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Determine if appointment is upcoming or past based on date
  const now = new Date();
  const upcomingAppointments = appointments.filter((apt) => {
    const aptDate = new Date(apt.appointment_date);
    return aptDate >= now;
  });
  const pastAppointments = appointments.filter((apt) => {
    const aptDate = new Date(apt.appointment_date);
    return aptDate < now;
  });

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-slate-900 mb-3">My Appointments</h1>
          <p className="text-slate-600">
            View your upcoming and past appointments
          </p>
        </div>

        {/* Search Form */}
        <Card className="mb-8">
          <CardHeader>
            <h2 className="text-slate-900">Find Your Appointments</h2>
            <p className="text-slate-600">
              Enter your details to view your appointment history
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Smith"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
              </div>

              <Button type="submit" size="lg" disabled={isLoading}>
                <User className="w-5 h-5 mr-2" />
                {isLoading ? 'Searching...' : 'View My Appointments'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        {searched && (
          <>
            {appointments.length === 0 ? (
              <Card className="bg-amber-50 border-amber-200">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 text-amber-800">
                    <AlertCircle className="w-6 h-6" />
                    <div>
                      <p className="text-amber-900">No appointments found</p>
                      <p className="text-amber-700">
                        We couldn't find any appointments for the provided information. Please check your details and try again.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <>
                {/* Upcoming Appointments */}
                {upcomingAppointments.length > 0 && (
                  <div className="mb-8">
                    <h2 className="text-slate-900 mb-4">Upcoming Appointments</h2>
                    <div className="space-y-4">
                      {upcomingAppointments.map((appointment) => (
                        <Card key={appointment.id} className="border-l-4 border-l-blue-600">
                          <CardContent className="pt-6">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                              <div className="space-y-3 flex-1">
                                <div className="flex items-center gap-2">
                                  <h3 className="text-slate-900">{appointment.patient_name}</h3>
                                  <Badge className="bg-blue-100 text-blue-700">
                                    {appointment.status || 'Scheduled'}
                                  </Badge>
                                </div>
                                
                                <div className="flex flex-wrap gap-4 text-slate-600">
                                  <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    <span>
                                      {new Date(appointment.appointment_date).toLocaleDateString('en-US', {
                                        weekday: 'long',
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric',
                                      })}
                                    </span>
                                  </div>
                                  
                                  <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    <span>{appointment.appointment_time}</span>
                                  </div>
                                </div>
                              </div>
                              
                              <Button variant="outline">
                                Reschedule
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Past Appointments */}
                {pastAppointments.length > 0 && (
                  <div>
                    <h2 className="text-slate-900 mb-4">Past Appointments</h2>
                    <div className="space-y-4">
                      {pastAppointments.map((appointment) => (
                        <Card key={appointment.id} className="border-l-4 border-l-slate-300 opacity-75">
                          <CardContent className="pt-6">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                              <div className="space-y-3 flex-1">
                                <div className="flex items-center gap-2">
                                  <h3 className="text-slate-900">{appointment.patient_name}</h3>
                                  <Badge variant="outline" className="text-slate-600">
                                    {appointment.status || 'Completed'}
                                  </Badge>
                                  <Badge className="bg-green-100 text-green-700">
                                    Completed
                                  </Badge>
                                </div>
                                
                                <div className="flex flex-wrap gap-4 text-slate-600">
                                  <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    <span>
                                      {new Date(appointment.appointment_date).toLocaleDateString('en-US', {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric',
                                      })}
                                    </span>
                                  </div>
                                  
                                  <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    <span>{appointment.appointment_time}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
