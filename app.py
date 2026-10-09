import streamlit as st
from datetime import datetime, timedelta
import json

st.set_page_config(page_title='Marley Coffee | Hub B2B · Demo', page_icon='☕', layout='wide')
st.markdown('''<style>.stApp{background:#F5F3EF;color:#241C18}h1,h2,h3{color:#241C18}div.stButton>button[kind="primary"]{background:#3E2723;color:white;border:0} .stMetric{background:#fff;padding:12px;border-radius:12px}</style>''', unsafe_allow_html=True)

PRODUCTS = {'Café en grano 1 kg': 18900, 'Café molido 500 g': 10900, 'Cápsulas (caja)': 8900}
MACHINES = ['Máquina OCS - Oficina Central', 'Máquina OCS - Sala de reuniones']

def init():
    defaults = {'role':None,'page':'Inicio','cart':{},'cart_version':0,'last_order_id':None,'checkout_delivery':'Despacho a domicilio (simulado)','orders':[{'id':'PED-001','fecha':'2026-09-12','detalle':'Café en grano 1 kg × 4','estado':'Entregado'}], 'tickets':[{'id':'OCS-001','equipo':MACHINES[0],'detalle':'Revisión preventiva (ejemplo)','estado':'Cerrado'}]}
    for key,val in defaults.items():
        if key not in st.session_state: st.session_state[key]=val
init()

st.caption('PROTOTIPO ACADÉMICO · DATOS FICTICIOS · SIN CONEXIÓN A MARLEY COFFEE NI DICALLA SPA')
st.title('☕ Marley Coffee | Hub de Autogestión B2B')
st.write('Demostración funcional de portal web responsive para HORECA y OCS.')

if st.session_state.role is None:
    st.subheader('Acceso de demostración')
    with st.form('login'):
        role = st.selectbox('Perfil de cliente', ['HORECA — Restaurante / cafetería', 'OCS — Oficina / empresa'])
        company = st.text_input('Empresa (ficticia)', value='Cliente de demostración')
        st.caption('No ingreses RUT ni contraseñas reales. Este acceso es solo una simulación.')
        submit=st.form_submit_button('Ingresar al portal', type='primary')
    if submit:
        st.session_state.role='HORECA' if role.startswith('HORECA') else 'OCS'
        st.session_state.company=company
        st.session_state.page='Inicio'
        st.rerun()
    st.stop()

with st.sidebar:
    st.subheader(st.session_state.company)
    st.caption('Perfil: '+st.session_state.role)
    menu = ['Inicio','Reposición','Confirmación','Historial'] if st.session_state.role=='HORECA' else ['Inicio','Reportar falla','Seguimiento']
    page=st.radio('Navegación', menu, index=menu.index(st.session_state.page) if st.session_state.page in menu else 0)
    st.session_state.page=page
    if st.button('Cerrar sesión'):
        st.session_state.role=None
        st.session_state.page='Inicio'
        st.rerun()

role=st.session_state.role
page=st.session_state.page
if role=='HORECA':
    if page=='Inicio':
        st.header('Dashboard HORECA')
        a,b,c=st.columns(3)
        a.metric('Pedidos de ejemplo',len(st.session_state.orders))
        b.metric('Productos disponibles',len(PRODUCTS))
        c.metric('Carrito actual',sum(st.session_state.cart.values()))
        st.info('Este panel simula el acceso a reposición e historial del cliente empresa.')
        if st.button('Ir a reposición',type='primary'):
            st.session_state.page='Reposición';st.rerun()
    elif page=='Reposición':
        st.header('Reposición HORECA')
        st.write('Modifica cantidades y confirma un pedido de prueba. No se realizará ninguna compra real.')
        st.caption('Los importes se recalculan automáticamente al cambiar cualquier cantidad.')
        qty = {}
        for i, (product, price) in enumerate(PRODUCTS.items()):
            qty[product] = st.number_input(
                f'{product} · Precio ficticio ${price:,.0f} CLP'.replace(',', '.'),
                min_value=0, max_value=100,
                value=st.session_state.cart.get(product, 0),
                step=1, key=f'auto_qty_{st.session_state.cart_version}_{i}',
            )
        # Los controles están fuera de st.form: cada cambio dispara un rerun.
        # Solo se lee su valor y se calcula el total, sin modificar sus claves.
        st.session_state.cart = qty.copy()
        total = sum(PRODUCTS[p] * q for p, q in qty.items())
        st.subheader('Resumen del carrito')
        for p, q in qty.items():
            if q:
                subtotal = PRODUCTS[p] * q
                st.write(f'{p}: {q} × ${PRODUCTS[p]:,.0f} = ${subtotal:,.0f}'.replace(',', '.'))
        if not total:
            st.info('Agrega productos con el botón + para ver el total.')
        st.metric('Total ilustrativo (CLP)', f'${total:,.0f}'.replace(',', '.'))
        st.divider()
        st.subheader('Entrega y condiciones del pedido')
        delivery = st.radio('Modalidad de entrega', ['Despacho a domicilio (simulado)', 'Retiro en punto habilitado (simulado)'], key='checkout_delivery')
        st.caption('Los plazos son ejemplos académicos: no representan disponibilidad ni compromisos reales de Marley Coffee.')
        if delivery.startswith('Despacho'):
            st.info('Entrega estimada ficticia: 2 a 4 días hábiles desde la confirmación. El horario exacto requeriría coordinación logística real.')
        else:
            st.info('Retiro ilustrativo: sujeto a preparación y confirmación del punto de retiro. No se ha habilitado ningún local real.')
        if st.button('Confirmar pedido simulado',type='primary',disabled=total==0):
            now=datetime.now()
            items=[{'producto':p,'cantidad':q,'precio_unitario':PRODUCTS[p],'subtotal':PRODUCTS[p]*q} for p,q in qty.items() if q]
            order_id=f'PED-{len(st.session_state.orders)+1:03d}'
            eta=now+timedelta(days=3 if delivery.startswith('Despacho') else 1)
            order={'id':order_id,'fecha':now.strftime('%Y-%m-%d %H:%M'), 'empresa':st.session_state.company,
                   'detalle':', '.join(f'{x["producto"]} × {x["cantidad"]}' for x in items),
                   'estado':'Pedido recibido (simulado)', 'items':items,'total':total,
                   'entrega':delivery,'estimacion':eta.strftime('%d-%m-%Y'),
                   'convenio':'Condiciones comerciales ficticias de demostración',
                   'documento':'Comprobante de demostración — NO es factura tributaria'}
            st.session_state.orders.insert(0,order)
            st.session_state.last_order_id=order_id
            st.session_state.cart={}
            st.session_state.cart_version+=1
            st.session_state.page='Confirmación'
            st.rerun()
    elif page=='Confirmación':
        st.header('Pedido confirmado · Demostración')
        order=next((o for o in st.session_state.orders if o['id']==st.session_state.last_order_id),None)
        if not order or 'items' not in order:
            st.info('Todavía no hay un pedido nuevo confirmado en esta sesión. Realiza una reposición para ver el comprobante.')
        else:
            st.success(f'Pedido {order["id"]} registrado correctamente en esta sesión de prueba.')
            a,b,c=st.columns(3)
            a.metric('Número de pedido',order['id'])
            b.metric('Total simulado',f'${order["total"]:,.0f}'.replace(',','.'))
            c.metric('Estado','Recibido')
            st.subheader('Comprobante de pedido — NO es factura tributaria')
            st.write('**Cliente empresa:**',order['empresa'])
            st.write('**Fecha y hora de registro:**',order['fecha'])
            st.write('**Convenio:**',order['convenio'])
            st.write('**Entrega seleccionada:**',order['entrega'])
            st.write('**Fecha referencial de entrega o retiro:**',order['estimacion'])
            st.caption('Fecha ficticia calculada para demostrar el flujo; no existe coordinación logística ni hora comprometida.')
            st.dataframe(order['items'],use_container_width=True,hide_index=True,
                         column_config={'producto':'Producto','cantidad':'Cantidad','precio_unitario':st.column_config.NumberColumn('Precio unitario (CLP)',format='$%d'),'subtotal':st.column_config.NumberColumn('Subtotal (CLP)',format='$%d')})
            st.subheader('Seguimiento y postventa (simulados)')
            st.write('① Pedido recibido → ② Preparación pendiente → ③ Despacho/retiro pendiente → ④ Entrega pendiente')
            st.info('En esta demostración el pedido queda en estado «Recibido». Los siguientes estados no se actualizan mediante una operación real.')
            receipt={'aviso':'DOCUMENTO DEMOSTRATIVO - NO ES FACTURA TRIBUTARIA',**order}
            st.download_button('Descargar comprobante de prueba (JSON)',data=json.dumps(receipt,ensure_ascii=False,indent=2),
                               file_name=f'{order["id"]}_demo.json',mime='application/json')
            if st.button('Volver a reposición'):
                st.session_state.page='Reposición';st.rerun()
    else:
        st.header('Historial de pedidos')
        st.dataframe([{k:o.get(k,'—') for k in ('id','fecha','detalle','estado','total','estimacion')} for o in st.session_state.orders],use_container_width=True,hide_index=True)
        st.caption('Los documentos contables y facturas tributarias reales requieren integración y emisión autorizada. Los pedidos nuevos son temporales y simulados.')
        if st.session_state.last_order_id and st.button('Ver comprobante del último pedido'):
            st.session_state.page='Confirmación';st.rerun()
else:
    if page=='Inicio':
        st.header('Estado de equipos OCS')
        st.info('Estados de ejemplo; no existe telemetría ni conexión a máquinas reales.')
        for machine in MACHINES:
            with st.container(border=True):
                st.subheader('☕ '+machine)
                st.write('Estado ilustrativo: operativo / pendiente de verificación')
        if st.button('Reportar una incidencia',type='primary'):
            st.session_state.page='Reportar falla';st.rerun()
    elif page=='Reportar falla':
        st.header('Reportar falla OCS')
        with st.form('ticket'):
            machine=st.selectbox('Equipo',MACHINES)
            problem=st.selectbox('Tipo de incidencia',['No dispensa café','No enciende','Fuga de agua','Otro'])
            detail=st.text_area('Descripción (sin datos personales)')
            send=st.form_submit_button('Crear ticket simulado',type='primary')
        if send:
            ticket_id=f'OCS-{len(st.session_state.tickets)+1:03d}'
            st.session_state.tickets.insert(0,{'id':ticket_id,'equipo':machine,'detalle':problem+(' — '+detail if detail else ''),'estado':'Recibido (simulado)'})
            st.success(f'Ticket {ticket_id} creado. Revisa Seguimiento.')
    else:
        st.header('Seguimiento de tickets')
        st.dataframe(st.session_state.tickets,use_container_width=True,hide_index=True)
        st.caption('Los estados se almacenan solo en esta sesión; no se envían a un proveedor técnico.')

st.divider()
st.caption('Proyecto académico · Duoc UC · Marley Coffee / Dicalla SpA (caso de estudio). MVP de demostración, no servicio oficial.')
