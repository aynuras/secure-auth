import { Component } from '@angular/core';
import { LogoComponent } from '../../../../shared/components/logo/logo.component';
import { NavbarComponent } from '../../../../shared/components/navbar/navbar.component';
import { GithubButtonComponent } from '../../../../shared/components/github-button/github-button.component';

@Component({
  selector: 'app-hero',
  imports: [LogoComponent, NavbarComponent, GithubButtonComponent],
  templateUrl: './hero.component.html',
  styleUrl: './hero.component.css',
})
export class HeroComponent {}
