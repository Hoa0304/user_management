'use client';

import { useState } from "react";
import UserModal from "../Form";

export default function Header() {
  const [open, setOpen] = useState(false);
  return (
    <header className="flex justify-between bg-white items-center px-100 p-5 mb-10">
      <div>
        <h1 className="text-2xl font-bold">User Management</h1>
        <p className="text-sm text-muted-foreground">
          Manage users and their platform access
        </p>
      </div>
      <UserModal
        mode="create"
        open={open}
        setOpen={setOpen}
        defaultValues={undefined}
        onSuccess={() => setOpen(false)}
      />
    </header>
  );
}
