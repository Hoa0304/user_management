'use client';

import CreateUserModal from "../Form";


export default function Header() {
  return (
    <header className="flex justify-between bg-white items-center px-100 p-5 mb-10">
      <div>
        <h1 className="text-2xl font-bold">User Management</h1>
        <p className="text-sm text-muted-foreground">
          Manage users and their platform access
        </p>
      </div>
      <CreateUserModal />
    </header>
  );
}
