import { Component } from '@angular/core';
import { HeroComponent } from './components/hero/hero.component';
import { FeaturesComponent } from './components/features/features.component';
import { ArchitectureComponent } from './components/architecture/architecture.component';
import { DiagramComponent } from './components/diagram/diagram.component';
import { SecurityDetailsComponent } from './components/securityDetails/securityDetails.component';
import { FooterComponent } from './components/footer/footer.component';

@Component({
  selector: 'app-landingPage',
  standalone: true,
  imports: [
    HeroComponent,
    FeaturesComponent,
    ArchitectureComponent,
    DiagramComponent,
    SecurityDetailsComponent,
    FooterComponent,
  ],
  templateUrl: './landingPage.component.html',
})
export class LandingPageComponent {}
