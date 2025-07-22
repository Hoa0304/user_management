'use client';

import Header from '@/components/module/Header';
import UserTable from '@/components/module/UserTable';
import { useUserQuery } from '@/hooks/useUserQuery';

export default function HomePage() {
  const { data: users, isLoading } = useUserQuery();

  return (
    <div>
      <Header />
      {isLoading ? <div>Loading...</div> : <UserTable users={users || []} />}
    </div>
  );
}
