'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Pencil, Trash2, Users } from 'lucide-react';
import { useUserQuery } from '@/hooks/useUserQuery';
import UserModal from './Form';
import { User } from '@/types/user';

import { colorMap, iconMap } from '@/lib/constants';
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
  AlertDialogDescription,
} from '@/components/ui/alert-dialog';
import axios from 'axios';

export default function UserTable() {
  const { data: users = [], isLoading, isError, refetch } = useUserQuery();

  const [editOpen, setEditOpen] = useState(false);

  const [editUser, setEditUser] = useState<User | undefined>();
  const [deleteUser, setDeleteUser] = useState<User | null>(null);

  const handleEdit = (user: User) => {
    setEditUser(user);
    setEditOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteUser) return;

    try {
      await axios.delete(`http://localhost:8000/api/users/${deleteUser.username}`);
      refetch();
    } catch (error) {
      console.error('Delete failed', error);
    } finally {
      setDeleteUser(null);
    }
  };

  if (isLoading) return <div className="px-6 py-4">Loading...</div>;
  if (isError) return <div className="px-6 py-4 text-red-500">Failed to load users.</div>;

  return (
    <div className="space-y-4 px-100">
      <Input placeholder="Search users by username or email..." className="p-5 bg-white" />
      <div className="text-sm mb-4 rounded-xl border shadow-sm bg-white py-5 text-muted-foreground flex items-center gap-2 pl-3">
        <Users className="w-4 h-4" />
        Total Users: <span className="font-semibold">{users.length}</span>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="max-h-[500px] overflow-y-auto scroll-hidden">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-2">User</th>
                  <th>Email</th>
                  <th>Platforms</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-muted/50">
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        {user.avatar ? (
                          <img src={user.avatar} alt={user.username} className="w-8 h-8 rounded-full object-cover" />
                        ) : (
                          <div
                            className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                            style={{ background: 'linear-gradient(to bottom right, #b721ff, #21d4fd)' }}
                          >
                            {user.username?.charAt(0).toUpperCase()}
                          </div>
                        )}
                        <span>{user.username}</span>
                      </div>
                    </td>
                    <td className="py-2">{user.email}</td>
                    <td className="py-2">
                      <div className="flex gap-1 flex-wrap">
                        {(user.platforms || []).map((p, idx) => (
                          <div
                            key={idx}
                            className="w-6 h-6 rounded-md flex items-center justify-center"
                            style={{ backgroundColor: colorMap[p.platform] || '#666' }}
                          >
                            <div className="text-white">{iconMap[p.platform] || '?'}</div>
                          </div>
                        ))}

                      </div>
                    </td>
                    <td className="py-2">
                      {user.created_at ? new Date(user.created_at).toISOString().slice(0, 10) : '-'}
                    </td>
                    <td>
                      <Button size="icon" variant="ghost" onClick={() => handleEdit(user)}>
                        <Pencil className="w-4 h-4 text-blue-500" />
                      </Button>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => setDeleteUser(user)}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>
                              Delete user {deleteUser?.username}?
                            </AlertDialogTitle>
                            <AlertDialogDescription>
                              This action cannot be undone. This will permanently delete this user from the system.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel onClick={() => setDeleteUser(null)}>Cancel</AlertDialogCancel>
                            <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Modal for Editing */}
      {editOpen && (
        <UserModal
          mode="edit"
          open={editOpen}
          setOpen={setEditOpen}
          defaultValues={editUser}
          onSuccess={refetch}
        />
      )}
    </div>
  );
}
