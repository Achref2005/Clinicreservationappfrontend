import { useState } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Calendar, Clock, User, AlertCircle } from 'lucide-react';

interface Appointment {
  id: string;
  patientName: string;
  date: string;
  time: string;
  doctor: string;
  specialty: string;
  status: 'upcoming' | 'completed';
}

// Mock data - In production, this would come from a database
const mockAppointments: Appointment[] = [
  {
    id: '1',
    patientName: 'John Smith',
    date: '2025-11-25',
    time: '10:00 AM',
    doctor: 'Dr. Sarah Johnson',
    specialty: 'Cardiology',
    status: 'upcoming',
  },
  {
    id: '2',
    patientName: 'John Smith',
    date: '2025-12-02',
    time: '2:30 PM',
    doctor: 'Dr. Emily Rodriguez',
    specialty: 'Dermatology',
    status: 'upcoming',
  },
  {
    id: '3',
    patientName: 'John Smith',
    date: '2025-10-15',
    time: '11:00 AM',
    doctor: 'Dr. Lisa Anderson',
    specialty: 'Internal Medicine',
    status: 'completed',
  },
  {
    id: '4',
    patientName: 'John Smith',
    date: '2025-09-20',
    time: '3:00 PM',
    doctor: 'Dr. Michael Chen',
    specialty: 'Pediatrics',
    status: 'completed',
  },
];

export function AppointmentsPage() {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Filter appointments by name (case-insensitive)
    const filtered = mockAppointments.filter(
      (apt) => apt.patientName.toLowerCase().includes(name.toLowerCase())
    );
    
    setAppointments(filtered);
    setSearched(true);
  };

  const upcomingAppointments = appointments.filter((apt) => apt.status === 'upcoming');
  const pastAppointments = appointments.filter((apt) => apt.status === 'completed');

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
                  <Label htmlFor="age">Age *</Label>
                  <Input
                    id="age"
                    type="number"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="25"
                    required
                  />
                </div>
              </div>

              <Button type="submit" size="lg">
                <User className="w-5 h-5 mr-2" />
                View My Appointments
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
                        We couldn't find any appointments for "{name}". Please check your details and try again.
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
                                  <h3 className="text-slate-900">{appointment.doctor}</h3>
                                  <Badge className="bg-blue-100 text-blue-700">
                                    {appointment.specialty}
                                  </Badge>
                                </div>
                                
                                <div className="flex flex-wrap gap-4 text-slate-600">
                                  <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    <span>
                                      {new Date(appointment.date).toLocaleDateString('en-US', {
                                        weekday: 'long',
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric',
                                      })}
                                    </span>
                                  </div>
                                  
                                  <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    <span>{appointment.time}</span>
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
                                  <h3 className="text-slate-900">{appointment.doctor}</h3>
                                  <Badge variant="outline" className="text-slate-600">
                                    {appointment.specialty}
                                  </Badge>
                                  <Badge className="bg-green-100 text-green-700">
                                    Completed
                                  </Badge>
                                </div>
                                
                                <div className="flex flex-wrap gap-4 text-slate-600">
                                  <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    <span>
                                      {new Date(appointment.date).toLocaleDateString('en-US', {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric',
                                      })}
                                    </span>
                                  </div>
                                  
                                  <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    <span>{appointment.time}</span>
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
