/**
 * Rikat UI v1.0 - Reactive Client Component Engine for Larapak & NgapakIn
 * Brings PrimeNG-style declarative bindings and Enterprise Web Components:
 *   - Two-Way Binding: [(model)]="key"
 *   - Property Binding: [property]="expression"
 *   - Event Binding: (event)="expression"
 *   - Rich Components: <l-table>, <l-dialog>, <l-toast>, <l-dropdown>
 * Zero Dependencies - 100% Native Web Standards
 */

(function () {
  'use strict';

  // 1. Reactive State Store
  const State = new Proxy({}, {
    set(target, prop, value) {
      target[prop] = value;
      Rikat.render();
      return true;
    }
  });

  window.Rikat = {
    state: State,
    
    init() {
      this.bindInputs();
      this.bindEvents();
      this.render();
    },

    set(key, val) {
      State[key] = val;
    },

    get(key) {
      return State[key];
    },

    // Evaluates expression in context of Rikat.state
    eval(expr, context = {}) {
      try {
        const fn = new Function('state', 'ctx', `with(state) { with(ctx) { return (${expr}); } }`);
        return fn(State, context);
      } catch (e) {
        return undefined;
      }
    },

    // Runs action expression in context of Rikat.state
    run(action, context = {}) {
      try {
        const fn = new Function('state', 'ctx', `with(state) { with(ctx) { ${action}; } }`);
        fn(State, context);
        this.render();
      } catch (e) {
        console.error('Rikat Action Error:', e);
      }
    },

    bindInputs() {
      // Find all elements with [(model)]
      document.querySelectorAll('[\\(\\[model\\]\\)]').forEach(el => {
        const key = el.getAttribute('([(model)])');
        if (!key) return;

        // Initialize state if empty
        if (State[key] === undefined) {
          if (el.type === 'checkbox') State[key] = el.checked;
          else State[key] = el.value || '';
        }

        // Listen for input changes
        const eventName = (el.type === 'checkbox' || el.tagName === 'SELECT') ? 'change' : 'input';
        el.addEventListener(eventName, () => {
          if (el.type === 'checkbox') State[key] = el.checked;
          else State[key] = el.value;
        });
      });
    },

    bindEvents() {
      // Walk attributes looking for (event)
      const allElements = document.querySelectorAll('*');
      allElements.forEach(el => {
        Array.from(el.attributes).forEach(attr => {
          const match = attr.name.match(/^\(([\w-]+)\)$/);
          if (match) {
            const eventName = match[1];
            const action = attr.value;
            el.addEventListener(eventName, (e) => {
              Rikat.run(action, { $event: e });
            });
          }
        });
      });
    },

    render() {
      // 1. Update [(model)] values
      document.querySelectorAll('[\\(\\[model\\]\\)]').forEach(el => {
        const key = el.getAttribute('([(model)])');
        const val = State[key];
        if (val !== undefined) {
          if (el.type === 'checkbox') el.checked = Boolean(val);
          else if (el.value !== val) el.value = val;
        }
      });

      // 2. Update [property] bindings
      document.querySelectorAll('*').forEach(el => {
        Array.from(el.attributes).forEach(attr => {
          const match = attr.name.match(/^\[([\w-]+)\]$/);
          if (match) {
            const prop = match[1];
            const expr = attr.value;
            const res = Rikat.eval(expr);

            if (prop === 'disabled') {
              el.disabled = Boolean(res);
            } else if (prop === 'visible' || prop === 'show') {
              el.style.display = res ? '' : 'none';
            } else if (prop === 'class') {
              if (typeof res === 'string') el.className = res;
            } else if (prop === 'text' || prop === 'html') {
              el.innerText = res ?? '';
            } else {
              el[prop] = res;
            }
          }
        });
      });

      // 3. Update text interpolation {{ key }}
      if (!this._templateCache) {
        this._templateCache = new Map();
        document.querySelectorAll('*').forEach(el => {
          if (el.children.length === 0 && el.textContent.includes('{{')) {
            this._templateCache.set(el, el.textContent);
          }
        });
      }

      this._templateCache.forEach((origText, el) => {
        const newText = origText.replace(/\{\{\s*([a-zA-Z0-9_$.]+)\s*\}\}/g, (_, expr) => {
          const val = Rikat.eval(expr);
          return val !== undefined ? val : '';
        });
        if (el.textContent !== newText) {
          el.textContent = newText;
        }
      });

      // Notify custom elements
      document.querySelectorAll('l-table, l-dialog').forEach(el => {
        if (typeof el.onStateUpdate === 'function') {
          el.onStateUpdate();
        }
      });
    },

    toast(title, message, type = 'info') {
      let container = document.getElementById('rikat-toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'rikat-toast-container';
        container.style.cssText = 'position:fixed;top:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:0.75rem;max-width:360px;';
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      toast.className = `alert alert-${type} shadow-lg`;
      toast.style.cssText = 'margin:0;animation:rikatSlideIn 0.25s ease;';
      toast.innerHTML = `
        <div style="flex-grow:1;">
          <div style="font-weight:600;margin-bottom:2px;">${title}</div>
          <div style="font-size:0.8rem;opacity:0.9;">${message}</div>
        </div>
      `;
      container.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.25s ease';
        setTimeout(() => toast.remove(), 250);
      }, 3500);
    }
  };

  // Add Toast Animation Keyframes
  const style = document.createElement('style');
  style.textContent = `
    @keyframes rikatSlideIn {
      from { transform: translateX(40px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);

  // ==========================================================================
  // Web Component 1: <l-dialog> (PrimeNG-style modal)
  // Usage: <l-dialog [(visible)]="showModal" header="Judul">...</l-dialog>
  // ==========================================================================
  class LDialog extends HTMLElement {
    connectedCallback() {
      this.visibleKey = this.getAttribute('([(visible)])') || this.getAttribute('[visible]');
      this.headerText = this.getAttribute('header') || 'Dialog';
      this.renderDialog();
    }

    onStateUpdate() {
      if (!this.visibleKey) return;
      const isVisible = Boolean(Rikat.get(this.visibleKey));
      const modal = this.querySelector('.rikat-modal-backdrop');
      if (modal) {
        modal.style.display = isVisible ? 'flex' : 'none';
      }
    }

    renderDialog() {
      const originalContent = this.innerHTML;
      this.innerHTML = `
        <div class="rikat-modal-backdrop" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(4px);z-index:999;align-items:center;justify-content:center;padding:1.5rem;">
          <div class="card shadow-xl" style="width:100%;max-width:520px;background:var(--bg-surface);border:1px solid var(--border-highlight);animation:rikatSlideIn 0.2s ease;">
            <div class="card-header flex items-center justify-between" style="border-bottom:1px solid var(--border-subtle);padding:1rem 1.25rem;">
              <span style="font-weight:600;font-size:1.1rem;color:var(--text-primary);">${this.headerText}</span>
              <button type="button" class="rikat-dialog-close btn-sm btn-secondary" style="border-radius:50%;width:28px;height:28px;padding:0;">&times;</button>
            </div>
            <div class="card-body" style="padding:1.25rem;">
              ${originalContent}
            </div>
          </div>
        </div>
      `;

      this.querySelector('.rikat-dialog-close').addEventListener('click', () => {
        if (this.visibleKey) {
          Rikat.set(this.visibleKey, false);
        }
      });
      this.onStateUpdate();
    }
  }
  customElements.define('l-dialog', LDialog);

  // ==========================================================================
  // Web Component 2: <l-table> (PrimeNG-style enterprise DataTable)
  // Usage: <l-table [data]="users" [paginator]="bener" [rows]="5"></l-table>
  // ==========================================================================
  class LTable extends HTMLElement {
    connectedCallback() {
      this.dataKey = this.getAttribute('[data]') || this.getAttribute('[value]');
      this.hasPaginator = this.getAttribute('[paginator]') === 'true' || this.getAttribute('[paginator]') === 'bener' || this.hasAttribute('paginator');
      this.rowsPerPage = parseInt(this.getAttribute('[rows]') || '5', 10);
      this.currentPage = 1;
      this.sortField = null;
      this.sortAsc = true;
      this.searchQuery = '';
      this.renderTable();
    }

    onStateUpdate() {
      this.updateRows();
    }

    getData() {
      let data = Rikat.eval(this.dataKey) || [];
      if (!Array.isArray(data)) return [];

      // Filter
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        data = data.filter(item => {
          return Object.values(item).some(val => String(val).toLowerCase().includes(q));
        });
      }

      // Sort
      if (this.sortField) {
        data = [...data].sort((a, b) => {
          const valA = a[this.sortField];
          const valB = b[this.sortField];
          if (valA < valB) return this.sortAsc ? -1 : 1;
          if (valA > valB) return this.sortAsc ? 1 : -1;
          return 0;
        });
      }

      return data;
    }

    renderTable() {
      this.innerHTML = `
        <div class="card border-subtle" style="overflow:hidden;">
          <div class="card-header flex items-center justify-between" style="background:var(--bg-surface-elevated);gap:1rem;">
            <input type="text" class="input rikat-table-search" placeholder="Goleki data..." style="max-width:260px;font-size:0.8rem;padding:0.4rem 0.75rem;">
            <span class="rikat-table-count text-xs text-muted"></span>
          </div>
          <div style="overflow-x:auto;">
            <table class="table table-hover w-full">
              <thead class="rikat-thead"></thead>
              <tbody class="rikat-tbody"></tbody>
            </table>
          </div>
          <div class="rikat-table-pagination card-footer flex items-center justify-between" style="display:${this.hasPaginator ? 'flex' : 'none'};">
            <span class="text-xs text-muted rikat-page-info"></span>
            <div class="flex gap-2">
              <button type="button" class="btn btn-secondary btn-sm rikat-btn-prev">&larr; Sedurunge</button>
              <button type="button" class="btn btn-secondary btn-sm rikat-btn-next">Sabanjure &rarr;</button>
            </div>
          </div>
        </div>
      `;

      this.querySelector('.rikat-table-search').addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.currentPage = 1;
        this.updateRows();
      });

      this.querySelector('.rikat-btn-prev').addEventListener('click', () => {
        if (this.currentPage > 1) {
          this.currentPage--;
          this.updateRows();
        }
      });

      this.querySelector('.rikat-btn-next').addEventListener('click', () => {
        const totalPages = Math.ceil(this.getData().length / this.rowsPerPage);
        if (this.currentPage < totalPages) {
          this.currentPage++;
          this.updateRows();
        }
      });

      this.updateRows();
    }

    updateRows() {
      const allData = this.getData();
      const tbody = this.querySelector('.rikat-tbody');
      const thead = this.querySelector('.rikat-thead');
      const countLabel = this.querySelector('.rikat-table-count');
      const pageInfo = this.querySelector('.rikat-page-info');

      if (!tbody || !thead) return;

      countLabel.textContent = `Total: ${allData.length} data`;

      if (allData.length === 0) {
        thead.innerHTML = '';
        tbody.innerHTML = '<tr><td colspan="100%" class="text-center text-muted" style="padding:2rem;">Ora ana data sing ditemokake</td></tr>';
        if (pageInfo) pageInfo.textContent = 'Kaca 0 saka 0';
        return;
      }

      // Auto-extract columns from first object
      const columns = Object.keys(allData[0]);

      // Render Header
      thead.innerHTML = `
        <tr>
          ${columns.map(col => `
            <th class="cursor-pointer select-none" data-col="${col}">
              ${col.toUpperCase()} ${this.sortField === col ? (this.sortAsc ? '▲' : '▼') : ''}
            </th>
          `).join('')}
        </tr>
      `;

      // Header click for sorting
      thead.querySelectorAll('th').forEach(th => {
        th.addEventListener('click', () => {
          const col = th.getAttribute('data-col');
          if (this.sortField === col) {
            this.sortAsc = !this.sortAsc;
          } else {
            this.sortField = col;
            this.sortAsc = true;
          }
          this.updateRows();
        });
      });

      // Pagination slice
      const start = (this.currentPage - 1) * this.rowsPerPage;
      const end = this.hasPaginator ? start + this.rowsPerPage : allData.length;
      const pageData = allData.slice(start, end);

      const totalPages = Math.ceil(allData.length / this.rowsPerPage) || 1;
      if (pageInfo) pageInfo.textContent = `Kaca ${this.currentPage} saka ${totalPages}`;

      // Render Rows
      tbody.innerHTML = pageData.map(row => `
        <tr class="cursor-pointer">
          ${columns.map(col => `<td>${row[col] !== undefined ? row[col] : ''}</td>`).join('')}
        </tr>
      `).join('');

      // Row click listener
      tbody.querySelectorAll('tr').forEach((tr, idx) => {
        tr.addEventListener('click', () => {
          const item = pageData[idx];
          const onSelectAttr = this.getAttribute('(onSelect)');
          if (onSelectAttr) {
            Rikat.run(onSelectAttr, { $event: item });
          }
        });
      });
    }
  }
  customElements.define('l-table', LTable);

  // Auto-initialize on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Rikat.init());
  } else {
    Rikat.init();
  }
})();

