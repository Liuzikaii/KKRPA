'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function HomePage() {
  const router = useRouter();
  const { loadFromStorage, isAuthenticated } = useAuthStore();

  useEffect(() => {
    loadFromStorage();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/workflows');
    } else {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
