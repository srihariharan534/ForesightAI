import * as React from 'react';
import { 
  User, 
  Lock, 
  Sliders, 
  Save, 
  ShieldCheck 
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { useToast } from '../components/ui/Toast';
import { useAppStore } from '../store/useAppStore';

export function Settings() {
  const { theme, setTheme } = useAppStore();
  const { toast } = useToast();

  const [profile, setProfile] = React.useState({
    name: 'Admin User',
    email: 'admin@foresight.ai',
    role: 'Chief Risk Officer (CRO)',
    org: 'Foresight Global Capital',
  });

  const [passwords, setPasswords] = React.useState({
    current: '',
    newPass: '',
    confirm: '',
  });

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: 'Profile Updated',
      description: 'Account settings have been saved successfully.',
      type: 'success',
    });
  };

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwords.newPass || passwords.newPass !== passwords.confirm) {
      toast({
        title: 'Validation Error',
        description: 'New password and confirmation must match.',
        type: 'error',
      });
      return;
    }
    setPasswords({ current: '', newPass: '', confirm: '' });
    toast({
      title: 'Password Changed',
      description: 'Security credentials updated.',
      type: 'success',
    });
  };

  return (
    <div className="space-y-6 animate-in max-w-4xl">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Settings</h1>
          <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
            Global Config
          </Badge>
        </div>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Manage identity, security parameters, system appearance, and institutional governance policies.
        </p>
      </div>

      <div className="space-y-6">
        {/* Profile Card */}
        <Card>
          <form onSubmit={handleSaveProfile}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <User className="h-4 w-4 text-primary" /> Profile & Identity
              </CardTitle>
              <CardDescription className="text-xs">
                Your organizational designation and administrative access level
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Full Name</label>
                  <Input 
                    value={profile.name} 
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })} 
                    className="text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Email Address</label>
                  <Input 
                    value={profile.email} 
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })} 
                    className="text-xs"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Role / Title</label>
                  <Input 
                    value={profile.role} 
                    onChange={(e) => setProfile({ ...profile, role: e.target.value })} 
                    className="text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Organization</label>
                  <Input 
                    value={profile.org} 
                    onChange={(e) => setProfile({ ...profile, org: e.target.value })} 
                    className="text-xs"
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end border-t border-slate-100 dark:border-slate-800 pt-4">
              <Button type="submit" size="sm" className="gap-1.5 text-xs">
                <Save className="h-3.5 w-3.5" /> Save Profile
              </Button>
            </CardFooter>
          </form>
        </Card>

        {/* Security & Password Card */}
        <Card>
          <form onSubmit={handlePasswordChange}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Lock className="h-4 w-4 text-primary" /> Security & Credentials
              </CardTitle>
              <CardDescription className="text-xs">
                Update account password and rotate API cryptographic keys
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Current Password</label>
                  <Input 
                    type="password" 
                    value={passwords.current} 
                    onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                    className="text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">New Password</label>
                  <Input 
                    type="password" 
                    value={passwords.newPass} 
                    onChange={(e) => setPasswords({ ...passwords, newPass: e.target.value })}
                    className="text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Confirm New Password</label>
                  <Input 
                    type="password" 
                    value={passwords.confirm} 
                    onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                    className="text-xs"
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end border-t border-slate-100 dark:border-slate-800 pt-4">
              <Button type="submit" variant="outline" size="sm" className="gap-1.5 text-xs">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" /> Update Password
              </Button>
            </CardFooter>
          </form>
        </Card>

        {/* Theme Preferences */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sliders className="h-4 w-4 text-primary" /> Display & UI Preferences
            </CardTitle>
            <CardDescription className="text-xs">
              Configure active system color mode and contrast levels
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              {(['light', 'dark', 'system'] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => {
                    setTheme(mode);
                    toast({ title: 'Theme Updated', description: `Switched to ${mode} mode.`, type: 'default' });
                  }}
                  className={`px-4 py-2 text-xs font-medium rounded-lg capitalize border transition-all ${
                    theme === mode 
                      ? 'border-primary bg-primary/10 text-primary font-bold' 
                      : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  {mode} Mode
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
