import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-google-button',
  standalone: true,
  imports: [CommonModule],
  styles: [':host { display: block; }'],
  template: `
    <button
      type="button"
      class="flex w-full items-center justify-center gap-3 rounded-lg border border-gray-700 bg-[#161b2c]/50 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-[#1f2937] hover:border-gray-600 transition-all duration-200 group cursor-pointer"
    >
      <svg
        class="h-5 w-5 grayscale group-hover:grayscale-0 transition-all duration-300"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          d="M12.0003 20.4501C16.8903 20.4501 20.9103 16.9201 21.8403 12.2301H12.0003V9.00012H23.5003C23.6403 9.80012 23.7503 10.6601 23.7503 11.6601C23.7503 18.2301 19.3403 22.9501 12.0003 22.9501C5.95029 22.9501 1.00029 18.0001 1.00029 12.0001C1.00029 6.00012 5.95029 1.05012 12.0003 1.05012C14.6703 1.05012 17.0603 1.95012 18.9403 3.69012L16.2703 6.36012C15.4203 5.58012 13.9803 4.77012 12.0003 4.77012C8.16029 4.77012 4.96029 8.04012 4.96029 12.0001C4.96029 15.9601 8.16029 19.2301 12.0003 19.2301V20.4501Z"
          fill="#EA4335"
        />
        <path
          d="M12.0003 20.4501C8.16029 20.4501 4.96029 17.1801 4.96029 13.2201H1.00029V12.0001H4.96029C4.96029 8.04012 8.16029 4.77012 12.0003 4.77012V1.05012C5.95029 1.05012 1.00029 6.00012 1.00029 12.0001C1.00029 18.0001 5.95029 22.9501 12.0003 22.9501V20.4501Z"
          fill="#34A853"
        />
        <path
          d="M21.8403 12.2301C20.9103 16.9201 16.8903 20.4501 12.0003 20.4501V22.9501C19.3403 22.9501 23.7503 18.2301 23.7503 11.6601H21.8403V12.2301Z"
          fill="#4285F4"
        />
        <path
          d="M23.5003 9.00012H12.0003V11.6601H21.8403C21.6503 13.1101 20.9903 14.4101 20.1003 15.4601L22.6903 17.6501C22.2503 18.1501 21.7503 18.6001 21.2103 19.0001C22.6803 17.3901 23.5003 15.1701 23.5003 11.6601C23.5003 10.6601 23.3903 9.80012 23.2503 9.00012H23.5003Z"
          fill="#FBBC05"
        />
      </svg>
      <ng-content>Google ile devam et</ng-content>
    </button>
  `,
})
export class GoogleButtonComponent {}
