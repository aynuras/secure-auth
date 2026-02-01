import { Component } from '@angular/core';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [MatMenuModule, MatButtonModule, MatIconModule, RouterModule],
  templateUrl: './navbar.component.html',
})
export class NavbarComponent {
  isMenuOpen: boolean = false;

  scrollTo(elementId: string): void {
    const element = document.getElementById(elementId);
    if (element) {
      const elementRect = element.getBoundingClientRect();
      const absoluteElementTop = elementRect.top + window.scrollY;
      const elementHeight = elementRect.height;
      const windowHeight = window.innerHeight;

      // Elementi ekranın tam ortasına hizala
      const targetPosition = absoluteElementTop - (windowHeight - elementHeight) / 2;

      this.smoothScrollTo(targetPosition, 1500);
    }
  }

  private smoothScrollTo(targetPosition: number, duration: number): void {
    const startPosition = window.scrollY;
    const distance = targetPosition - startPosition;
    let startTime: number | null = null;

    const animation = (currentTime: number) => {
      if (startTime === null) startTime = currentTime;
      const timeElapsed = currentTime - startTime;

      const nextScroll = this.easeInOutQuad(timeElapsed, startPosition, distance, duration);

      window.scrollTo(0, nextScroll);

      if (timeElapsed < duration) {
        requestAnimationFrame(animation);
      }
    };

    requestAnimationFrame(animation);
  }

  private easeInOutQuad(t: number, b: number, c: number, d: number): number {
    t /= d / 2;
    if (t < 1) return (c / 2) * t * t + b;
    t--;
    return (-c / 2) * (t * (t - 2) - 1) + b;
  }
}
