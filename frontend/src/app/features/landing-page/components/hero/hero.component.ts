import { Component } from '@angular/core';
import { LogoComponent } from '../../../../shared/components/logo/logo.component';
import { NavbarComponent } from '../../../../shared/components/navbar/navbar.component';
import { GithubButtonComponent } from '../../../../shared/components/github-button/github-button.component';
import { FloatingCardsComponent } from '../../../../shared/components/floating-cards/floating-cards.component';

@Component({
  selector: 'app-hero',
  imports: [LogoComponent, NavbarComponent, GithubButtonComponent, FloatingCardsComponent],
  templateUrl: './hero.component.html',
})
export class HeroComponent {}
