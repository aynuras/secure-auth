import { Component } from '@angular/core';
import { HeroComponent } from './components/hero/hero.component';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [HeroComponent],
  templateUrl: './landingPage.component.html',
  styleUrls: ['./landingPage.component.css'],
})
export class LandingPageComponent {}
