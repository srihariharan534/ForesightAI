
import { Plus, MoreHorizontal } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';

const users = [
  { id: 'usr_1', name: 'Alice Smith', email: 'alice@foresight.ai', role: 'Admin', status: 'Active', lastActive: '2 mins ago' },
  { id: 'usr_2', name: 'Bob Johnson', email: 'bob@foresight.ai', role: 'Analyst', status: 'Active', lastActive: '1 hour ago' },
  { id: 'usr_3', name: 'Carol Williams', email: 'carol@foresight.ai', role: 'Viewer', status: 'Inactive', lastActive: '3 days ago' },
  { id: 'usr_4', name: 'David Brown', email: 'david@foresight.ai', role: 'Engineer', status: 'Active', lastActive: '10 mins ago' },
];

export function Users() {
  return (
    <div className="space-y-6 animate-in">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">User Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage organization members, roles, and permissions.
          </p>
        </div>
        <Button className="gap-2"><Plus className="h-4 w-4" /> Add User</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Organization Members</CardTitle>
          <CardDescription>A list of all users in your organization.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <Input className="w-full max-w-sm" placeholder="Search users..." />
            <div className="flex gap-2">
              <Button variant="outline" size="sm">Filter by Role</Button>
              <Button variant="outline" size="sm">Filter by Status</Button>
            </div>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Active</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>
                    <Badge variant={user.status === 'Active' ? 'success' : 'secondary'}>
                      {user.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-500">{user.lastActive}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
