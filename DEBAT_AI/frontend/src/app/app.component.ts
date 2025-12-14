import { Component, OnInit, OnDestroy, Renderer2, Inject } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import { NavbarComponent } from './components/navbar/navbar.component';
import { DOCUMENT } from '@angular/common';
import { Subject } from 'rxjs';
import { takeUntil, filter, map } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private renderer: Renderer2,
    @Inject(DOCUMENT) private document: Document
  ) {}

  ngOnInit(): void {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      map(() => this.activatedRoute),
      map(route => {
        while (route.firstChild) {
          route = route.firstChild;
        }
        return route;
      }),
      filter(route => route.outlet === 'primary'),
      takeUntil(this.destroy$)
    ).subscribe(route => {
      this.document.body.classList.remove('homepage-background', 'debate-background');

      if (route.snapshot.url.length === 0 || route.snapshot.url[0].path === '') {
        this.renderer.addClass(this.document.body, 'homepage-background');
      } else if (route.snapshot.url[0].path === 'debates') {
        this.renderer.addClass(this.document.body, 'debate-background');
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
